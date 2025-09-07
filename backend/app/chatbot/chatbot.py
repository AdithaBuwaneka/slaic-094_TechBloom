from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from app.core.config import settings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from typing import Optional
from langsmith import Client
from langchain.callbacks import LangChainTracer

# Initialize LangSmith client
if settings.LANGCHAIN_API_KEY:
    try:
        langsmith_client = Client()
        tracer = LangChainTracer(project_name="rag-qa-system")
        print("LangSmith tracing enabled")
    except Exception:
        langsmith_client = None
        tracer = None
        print("LangSmith not configured")
else:
    langsmith_client = None
    tracer = None
    print("LangSmith not configured")

# Initialize router for chatbot endpoints
router = APIRouter()

# Global variables to store initialized components
vectordb = None
qa_chain = None

class QuestionRequest(BaseModel):
    question: str
    temperature: Optional[float] = 0.2

class QuestionResponse(BaseModel):
    question: str
    answer: str

def initialize_rag_system():
    """Initialize the RAG system components"""
    global vectordb, qa_chain
    
    try:
        # Get the path to the transit guide file in the chatbot directory
        current_dir = Path(__file__).parent
        guide_file_path = current_dir / "transit_app_guide.txt"
        
        # Load and split documents
        loader = TextLoader(str(guide_file_path))
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        
        print(f"Created {len(chunks)} document chunks")
        
        # Embeddings + Vector DB
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Vector database path in the chatbot directory
        db_path = current_dir / "db"
        
        # Check if vector database already exists
        if db_path.exists():
            vectordb = Chroma(persist_directory=str(db_path), embedding_function=embeddings)
            print("Loaded existing vector database")
        else:
            vectordb = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=str(db_path))
            print("Created new vector database")
        
        # LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.2,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )
        
        # Retrieval QA Chain with limited results
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})  # Limit to 3 results
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        
        print("RAG system initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing RAG system: {str(e)}")
        raise e

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG QA System is running!", "status": "healthy"}

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the RAG system
    """
    global qa_chain
    
    if qa_chain is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        # Update LLM temperature if different from default
        if request.temperature != 0.2:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                temperature=request.temperature,
                google_api_key=settings.GOOGLE_API_KEY,
                convert_system_message_to_human=True
            )
            retriever = vectordb.as_retriever(search_kwargs={"k": 2})  # Limit to 2 results
            qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        
        # Get answer from QA chain using invoke with LangSmith tracing
        if tracer:
            # Include LangSmith callback for tracing
            result = qa_chain.invoke(
                {"query": request.question},
                config={"callbacks": [tracer], "tags": ["rag-question"], "metadata": {"temperature": request.temperature}}
            )
        else:
            result = qa_chain.invoke({"query": request.question})
            
        answer = result["result"]
        print(f"Question: {request.question}\nAnswer: {answer}")
        
        # Log to LangSmith if available
        if langsmith_client:
            try:
                langsmith_client.create_run(
                    name="rag_question_answering",
                    inputs={"question": request.question, "temperature": request.temperature},
                    outputs={"answer": answer},
                    run_type="chain"
                )
            except Exception as ls_error:
                print(f"LangSmith logging error: {ls_error}")
        
        return QuestionResponse(question=request.question, answer=answer)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.get("/health")
async def health_check():
    """Detailed health check"""
    current_dir = Path(__file__).parent
    db_path = current_dir / "db"
    
    return {
        "status": "healthy",
        "rag_system_initialized": qa_chain is not None,
        "vector_db_exists": db_path.exists(),
        "langsmith_enabled": langsmith_client is not None
    }

@router.post("/reinitialize")
async def reinitialize_system():
    """Reinitialize the RAG system (useful if documents are updated)"""
    try:
        initialize_rag_system()
        return {"message": "RAG system reinitialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reinitializing system: {str(e)}")

# Initialize the RAG system when the module is loaded
initialize_rag_system()