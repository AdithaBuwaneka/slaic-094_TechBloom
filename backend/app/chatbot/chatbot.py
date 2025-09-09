# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import os
# from pathlib import Path
# from app.core.config import settings
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain.chains import RetrievalQA
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from typing import Optional
# from langsmith import Client
# from langchain.callbacks import LangChainTracer

# # Initialize LangSmith client
# if settings.LANGCHAIN_API_KEY:
#     try:
#         langsmith_client = Client()
#         tracer = LangChainTracer(project_name="rag-qa-system")
#         print("LangSmith tracing enabled")
#     except Exception:
#         langsmith_client = None
#         tracer = None
#         print("LangSmith not configured")
# else:
#     langsmith_client = None
#     tracer = None
#     print("LangSmith not configured")

# # Initialize router for chatbot endpoints
# router = APIRouter()

# # Global variables to store initialized components
# vectordb = None
# qa_chain = None

# class QuestionRequest(BaseModel):
#     question: str
#     temperature: Optional[float] = 0.2

# class QuestionResponse(BaseModel):
#     question: str
#     answer: str

# def initialize_rag_system():
#     """Initialize the RAG system components"""
#     global vectordb, qa_chain
    
#     try:
#         # Get the path to the transit guide file in the chatbot directory
#         current_dir = Path(__file__).parent
#         guide_file_path = current_dir / "transit_app_guide.txt"
        
#         # Load and split documents
#         loader = TextLoader(str(guide_file_path))
#         docs = loader.load()
#         splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#         chunks = splitter.split_documents(docs)
        
#         print(f"Created {len(chunks)} document chunks")
        
#         # Embeddings + Vector DB
#         embeddings = GoogleGenerativeAIEmbeddings(
#             model="models/embedding-001",
#             google_api_key=settings.GOOGLE_API_KEY
#         )
        
#         # Vector database path in the chatbot directory
#         db_path = current_dir / "db"
        
#         # Check if vector database already exists
#         if db_path.exists():
#             vectordb = Chroma(persist_directory=str(db_path), embedding_function=embeddings)
#             print("Loaded existing vector database")
#         else:
#             vectordb = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=str(db_path))
#             print("Created new vector database")
        
#         # LLM
#         llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-flash", 
#             temperature=0.2,
#             google_api_key=settings.GOOGLE_API_KEY,
#             convert_system_message_to_human=True
#         )
        
#         # Retrieval QA Chain with limited results
#         retriever = vectordb.as_retriever(search_kwargs={"k": 3})  # Limit to 3 results
#         qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        
#         print("RAG system initialized successfully!")
        
#     except Exception as e:
#         print(f"Error initializing RAG system: {str(e)}")
#         raise e

# @router.get("/")
# async def root():
#     """Health check endpoint"""
#     return {"message": "RAG QA System is running!", "status": "healthy"}

# @router.post("/ask", response_model=QuestionResponse)
# async def ask_question(request: QuestionRequest):
#     """
#     Ask a question to the RAG system
#     """
#     global qa_chain
    
#     if qa_chain is None:
#         raise HTTPException(status_code=500, detail="RAG system not initialized")
    
#     try:
#         # Update LLM temperature if different from default
#         if request.temperature != 0.2:
#             llm = ChatGoogleGenerativeAI(
#                 model="gemini-1.5-flash", 
#                 temperature=request.temperature,
#                 google_api_key=settings.GOOGLE_API_KEY,
#                 convert_system_message_to_human=True
#             )
#             retriever = vectordb.as_retriever(search_kwargs={"k": 2})  # Limit to 2 results
#             qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        
#         # Get answer from QA chain using invoke with LangSmith tracing
#         if tracer:
#             # Include LangSmith callback for tracing
#             result = qa_chain.invoke(
#                 {"query": request.question},
#                 config={"callbacks": [tracer], "tags": ["rag-question"], "metadata": {"temperature": request.temperature}}
#             )
#         else:
#             result = qa_chain.invoke({"query": request.question})
            
#         answer = result["result"]
#         print(f"Question: {request.question}\nAnswer: {answer}")
        
#         # Log to LangSmith if available
#         if langsmith_client:
#             try:
#                 langsmith_client.create_run(
#                     name="rag_question_answering",
#                     inputs={"question": request.question, "temperature": request.temperature},
#                     outputs={"answer": answer},
#                     run_type="chain"
#                 )
#             except Exception as ls_error:
#                 print(f"LangSmith logging error: {ls_error}")
        
#         return QuestionResponse(question=request.question, answer=answer)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# @router.get("/health")
# async def health_check():
#     """Detailed health check"""
#     current_dir = Path(__file__).parent
#     db_path = current_dir / "db"
    
#     return {
#         "status": "healthy",
#         "rag_system_initialized": qa_chain is not None,
#         "vector_db_exists": db_path.exists(),
#         "langsmith_enabled": langsmith_client is not None
#     }

# @router.post("/reinitialize")
# async def reinitialize_system():
#     """Reinitialize the RAG system (useful if documents are updated)"""
#     try:
#         initialize_rag_system()
#         return {"message": "RAG system reinitialized successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error reinitializing system: {str(e)}")

# # Initialize the RAG system when the module is loaded
# initialize_rag_system()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from app.core.config import settings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from typing import Optional, List, Dict, Any
from langsmith import Client
from langchain.callbacks import LangChainTracer
import hashlib
import json
from datetime import datetime, timedelta
import uuid
import re

# Initialize LangSmith client
if settings.LANGCHAIN_API_KEY:
    try:
        langsmith_client = Client()
        tracer = LangChainTracer(project_name="conversational-rag-system")
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
conversations: Dict[str, Any] = {}  # Store conversations in memory
response_cache: Dict[str, Dict] = {}  # Cache for responses

# Cache settings
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_SIZE = 1000

# Conversational patterns for detecting general chat vs app-specific queries
GREETING_PATTERNS = [
    r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
    r'\b(how are you|what\'s up|whats up)\b',
    r'\bmy name is\b',
    r'\bi am\b',
    r'\bcall me\b'
]

APP_RELATED_KEYWORDS = [
    'transit', 'transport', 'bus', 'train', 'route', 'journey', 'travel',
    'fare', 'schedule', 'timetable', 'delay', 'smart transit companion',
    'app', 'feature', 'agent', 'multilingual', 'accessibility', 'disruption',
    'planning', 'navigation', 'booking', 'payment', 'real-time', 'gps'
]

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ConversationRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_history_length: Optional[int] = 10

class ConversationResponse(BaseModel):
    message: str
    response: str
    session_id: str
    conversation_history: List[ChatMessage]
    response_type: str  # "general" or "app_specific"

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_active: str
    message_count: int
    user_name: Optional[str] = None

def is_greeting_or_general(message: str) -> bool:
    """Check if message is a greeting or general conversation"""
    message_lower = message.lower()
    
    # Check for greeting patterns
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, message_lower):
            return True
    
    # Check if message is very short and likely conversational
    if len(message.split()) <= 3 and not any(keyword in message_lower for keyword in APP_RELATED_KEYWORDS):
        return True
        
    return False

def is_app_related(message: str) -> bool:
    """Check if message is related to the Smart Transit Companion app"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in APP_RELATED_KEYWORDS)

def extract_user_name(message: str) -> Optional[str]:
    """Extract user name from introduction messages"""
    message_lower = message.lower()
    
    # Pattern: "my name is John" or "I am John" or "call me John"
    patterns = [
        r'my name is\s+([a-zA-Z]+)',
        r'i am\s+([a-zA-Z]+)',
        r'call me\s+([a-zA-Z]+)',
        r'i\'m\s+([a-zA-Z]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            return match.group(1).capitalize()
    
    return None

def generate_general_response(message: str, user_name: Optional[str] = None, conversation_context: List[BaseMessage] = None) -> str:
    """Generate responses for general conversation using LLM without RAG"""
    
    # Create a conversational prompt
    system_prompt = """You are a friendly and helpful assistant for the Smart Transit Companion app. 
    You can engage in general conversation while being ready to help users with transit and transportation questions.
    
    Key points about your personality:
    - You're warm, friendly, and conversational
    - You remember user names and personal details from the conversation
    - You can handle greetings, introductions, and casual chat naturally
    - When appropriate, you can mention that you're here to help with the Smart Transit Companion app
    - You don't always need to talk about the app - you can have normal conversations too
    
    Guidelines:
    - For greetings: Respond naturally and warmly
    - For introductions: Remember and use their name
    - For casual questions: Engage normally like a helpful assistant
    - Only mention the app context when it's natural or relevant
    - Keep responses concise but friendly
    """
    
    # Build context from recent conversation
    context_text = ""
    if conversation_context:
        recent_messages = conversation_context[-4:]  # Last 2 exchanges
        for msg in recent_messages:
            if isinstance(msg, HumanMessage):
                context_text += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                context_text += f"Assistant: {msg.content}\n"
    
    user_context = f"User's name: {user_name}\n" if user_name else ""
    
    prompt = f"""
    {system_prompt}
    
    {user_context}
    Recent conversation context:
    {context_text}
    
    Current user message: {message}
    
    Respond naturally and conversationally:
    """
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,  # Higher temperature for more natural conversation
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        # Fallback responses for common scenarios
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hi', 'hello', 'hey']):
            if user_name:
                return f"Hello {user_name}! Great to see you again. How can I help you today?"
            return "Hello! I'm your Smart Transit Companion assistant. How can I help you today?"
        
        if 'my name is' in message_lower or 'i am' in message_lower:
            name = extract_user_name(message)
            if name:
                return f"Nice to meet you, {name}! I'm here to help you with any questions about transportation or the Smart Transit Companion app. What would you like to know?"
        
        if any(word in message_lower for word in ['how are you', 'what\'s up', 'whats up']):
            return "I'm doing well, thank you for asking! I'm here and ready to help you with any questions about transportation or our Smart Transit Companion app. What can I assist you with?"
        
        return "I'm here to help! Feel free to ask me anything about transportation, route planning, or how to use the Smart Transit Companion app."

def generate_cache_key(question: str, session_id: str, temperature: float) -> str:
    """Generate a cache key for the question"""
    content = f"{question}_{session_id}_{temperature}"
    return hashlib.md5(content.encode()).hexdigest()

def clean_expired_cache():
    """Remove expired cache entries"""
    current_time = datetime.now()
    expired_keys = []
    
    for key, cache_entry in response_cache.items():
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        if current_time - cache_time > timedelta(hours=CACHE_EXPIRY_HOURS):
            expired_keys.append(key)
    
    for key in expired_keys:
        del response_cache[key]
    
    # If cache is still too large, remove oldest entries
    if len(response_cache) > MAX_CACHE_SIZE:
        sorted_cache = sorted(response_cache.items(), 
                            key=lambda x: x[1]["timestamp"])
        keys_to_remove = sorted_cache[:len(response_cache) - MAX_CACHE_SIZE]
        for key, _ in keys_to_remove:
            del response_cache[key]

def get_or_create_conversation(session_id: str, max_history_length: int = 10):
    """Get existing conversation or create new one"""
    if session_id not in conversations:
        conversations[session_id] = {
            "memory": ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=max_history_length  # Keep last k exchanges
            ),
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "message_count": 0,
            "user_name": None
        }
    else:
        conversations[session_id]["last_active"] = datetime.now().isoformat()
    
    return conversations[session_id]

def initialize_rag_system():
    """Initialize the RAG system components"""
    global vectordb
    
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
        
        print("RAG system initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing RAG system: {str(e)}")
        raise e

def create_conversational_chain(temperature: float = 0.2):
    """Create a conversational retrieval chain with better prompting"""
    
    # Custom prompt template for better context handling
    custom_prompt = PromptTemplate(
        template="""You are a helpful assistant for the Smart Transit Companion app in Sri Lanka. 
        Use the provided context to answer questions about the app, transportation, and travel planning.
        
        If the question is related to the app or transportation, use the context provided to give accurate information.
        If you don't find relevant information in the context, say so honestly and offer to help in other ways.
        
        Always be conversational, friendly, and helpful. Remember any personal details mentioned in the conversation.
        
        Context from Smart Transit Companion documentation:
        {context}
        
        Previous conversation:
        {chat_history}
        
        Current question: {question}
        
        Helpful Answer:""",
        input_variables=["context", "chat_history", "question"]
    )
    
    # LLM with appropriate temperature for app-specific responses
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=temperature,
        google_api_key=settings.GOOGLE_API_KEY,
        convert_system_message_to_human=True
    )
    
    # Retriever with limited results
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    # Create conversational chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        verbose=True,
        combine_docs_chain_kwargs={"prompt": custom_prompt}
    )
    
    return chain

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Conversational RAG QA System is running!", "status": "healthy"}

@router.post("/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """
    Chat with the conversational RAG system
    """
    global vectordb, conversations, response_cache
    
    if vectordb is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Clean expired cache periodically
        clean_expired_cache()
        
        # Get or create conversation
        conversation = get_or_create_conversation(request.session_id, request.max_history_length)
        
        # Extract and store user name if mentioned
        user_name = extract_user_name(request.message)
        if user_name:
            conversation["user_name"] = user_name
        
        # Get chat history for context
        chat_history = []
        if hasattr(conversation["memory"], 'chat_memory'):
            chat_history = conversation["memory"].chat_memory.messages
        
        # Determine if this is a general conversation or app-specific query
        is_general = is_greeting_or_general(request.message)
        is_app_query = is_app_related(request.message)
        
        response_type = "general"
        
        # Handle general conversation without RAG
        if is_general and not is_app_query:
            answer = generate_general_response(
                request.message, 
                conversation.get("user_name"),
                chat_history
            )
            response_type = "general"
            
        else:
            # Use RAG for app-specific queries
            response_type = "app_specific"
            
            # Check cache first for app queries
            cache_key = generate_cache_key(request.message, request.session_id, request.temperature)
            if cache_key in response_cache:
                cached_response = response_cache[cache_key]
                print(f"Cache hit for question: {request.message}")
                answer = cached_response["response"]
            else:
                # Create conversational chain
                chain = create_conversational_chain(request.temperature)
                
                # Get response from chain with LangSmith tracing
                if tracer:
                    result = chain.invoke({
                        "question": request.message,
                        "chat_history": chat_history
                    }, config={
                        "callbacks": [tracer], 
                        "tags": ["conversational-rag"], 
                        "metadata": {
                            "session_id": request.session_id,
                            "temperature": request.temperature
                        }
                    })
                else:
                    result = chain.invoke({
                        "question": request.message,
                        "chat_history": chat_history
                    })
                
                answer = result["answer"]
                
                # Cache the response for app queries
                response_cache[cache_key] = {
                    "response": answer,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": request.session_id
                }
        
        # Update conversation memory
        conversation["memory"].save_context(
            {"input": request.message},
            {"output": answer}
        )
        conversation["message_count"] += 1
        
        print(f"Question: {request.message}\nAnswer: {answer}")
        print(f"Session: {request.session_id}, Messages: {conversation['message_count']}, Type: {response_type}")
        
        # Log to LangSmith if available
        if langsmith_client:
            try:
                langsmith_client.create_run(
                    name="conversational_rag_chat",
                    inputs={
                        "message": request.message, 
                        "session_id": request.session_id,
                        "temperature": request.temperature,
                        "response_type": response_type
                    },
                    outputs={"response": answer},
                    run_type="chain"
                )
            except Exception as ls_error:
                print(f"LangSmith logging error: {ls_error}")
        
        # Convert memory to chat history for response
        chat_history_response = []
        if hasattr(conversation["memory"], 'chat_memory') and conversation["memory"].chat_memory.messages:
            for msg in conversation["memory"].chat_memory.messages:
                if isinstance(msg, HumanMessage):
                    chat_history_response.append(ChatMessage(
                        role="user", 
                        content=msg.content,
                        timestamp=datetime.now().isoformat()
                    ))
                elif isinstance(msg, AIMessage):
                    chat_history_response.append(ChatMessage(
                        role="assistant", 
                        content=msg.content,
                        timestamp=datetime.now().isoformat()
                    ))
        
        return ConversationResponse(
            message=request.message,
            response=answer,
            session_id=request.session_id,
            conversation_history=chat_history_response,
            response_type=response_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/sessions")
async def get_sessions():
    """Get all active sessions"""
    session_list = []
    for session_id, conversation in conversations.items():
        session_list.append(SessionInfo(
            session_id=session_id,
            created_at=conversation["created_at"],
            last_active=conversation["last_active"],
            message_count=conversation["message_count"],
            user_name=conversation.get("user_name")
        ))
    
    return {"sessions": session_list, "total_sessions": len(session_list)}

@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a specific session"""
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    
    conversation = conversations[session_id]
    chat_history = []
    
    if hasattr(conversation["memory"], 'chat_memory') and conversation["memory"].chat_memory.messages:
        for msg in conversation["memory"].chat_memory.messages:
            if isinstance(msg, HumanMessage):
                chat_history.append(ChatMessage(
                    role="user", 
                    content=msg.content,
                    timestamp=datetime.now().isoformat()
                ))
            elif isinstance(msg, AIMessage):
                chat_history.append(ChatMessage(
                    role="assistant", 
                    content=msg.content,
                    timestamp=datetime.now().isoformat()
                ))
    
    return {
        "session_id": session_id,
        "conversation_history": chat_history,
        "session_info": SessionInfo(
            session_id=session_id,
            created_at=conversation["created_at"],
            last_active=conversation["last_active"],
            message_count=conversation["message_count"],
            user_name=conversation.get("user_name")
        )
    }

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del conversations[session_id]
    
    # Also remove related cache entries
    keys_to_remove = [key for key in response_cache.keys() 
                     if response_cache[key].get("session_id") == session_id]
    for key in keys_to_remove:
        del response_cache[key]
    
    return {"message": f"Session {session_id} deleted successfully"}

@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """Clear conversation history for a specific session"""
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    
    conversation = conversations[session_id]
    conversation["memory"].clear()
    conversation["message_count"] = 0
    conversation["last_active"] = datetime.now().isoformat()
    # Keep user name even after clearing
    
    return {"message": f"Session {session_id} history cleared successfully"}

@router.get("/health")
async def health_check():
    """Detailed health check"""
    current_dir = Path(__file__).parent
    db_path = current_dir / "db"
    
    return {
        "status": "healthy",
        "rag_system_initialized": vectordb is not None,
        "vector_db_exists": db_path.exists(),
        "langsmith_enabled": langsmith_client is not None,
        "active_sessions": len(conversations),
        "cache_size": len(response_cache),
        "cache_hit_rate": "N/A"
    }

@router.post("/reinitialize")
async def reinitialize_system():
    """Reinitialize the RAG system (useful if documents are updated)"""
    try:
        initialize_rag_system()
        return {"message": "RAG system reinitialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reinitializing system: {str(e)}")

@router.post("/clear-cache")
async def clear_cache():
    """Clear all cached responses"""
    global response_cache
    cache_size = len(response_cache)
    response_cache.clear()
    return {"message": f"Cleared {cache_size} cached responses"}

# Initialize the RAG system when the module is loaded
initialize_rag_system()