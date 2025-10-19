from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from app.core.config import settings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from typing import Optional, Dict, Any
from langsmith import Client
from langchain.callbacks import LangChainTracer
import json
import re
from datetime import datetime
from app.core.database import db
import asyncio # ✅ Added for non-blocking sleep
import random

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
    temperature: Optional[float] = 0.5  # Default to more conversational, friendly responses
    user_id: Optional[str] = None

class IntentResponse(BaseModel):
    question: str
    answer: str
    intent_type: str
    action_data: Optional[Dict[str, Any]] = None
    requires_action: bool = False

def initialize_rag_system():
    """Initialize the RAG system components"""
    global vectordb, qa_chain
    
    try:
        try:
            import chromadb
        except ImportError:
            print("WARNING: chromadb not installed. Chatbot will be disabled.")
            vectordb = None
            qa_chain = None
            return
        
        current_dir = Path(__file__).parent
        guide_file_path = current_dir / "transit_app_guide.txt"
        
        loader = TextLoader(str(guide_file_path))
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        
        print(f"Created {len(chunks)} document chunks")
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_GEMINI_API_KEY
        )
        
        db_path = current_dir / "db"
        
        if db_path.exists():
            vectordb = Chroma(persist_directory=str(db_path), embedding_function=embeddings)
            print("Loaded existing vector database")
        else:
            vectordb = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=str(db_path))
            print("Created new vector database")
        
        system_prompt = """You are Smart Transit Companion, a friendly AI travel buddy helping people in Sri Lanka get around easily!

Your personality:
- Warm, friendly, and conversational (like chatting with a helpful friend)
- Use simple, everyday language (avoid technical jargon)
- Keep responses short and easy to read (2-4 sentences max)
- Use emojis occasionally to be friendly but do not overdo it
- Sound excited to help people travel better

CRITICAL RULES:
- You can ONLY answer questions about Sri Lankan public transportation, the Smart Transit Companion app, and related travel topics
- You must ONLY use information from the provided context/knowledge base
- If the answer is not in the provided context, say: I do not have that information in my knowledge base. I am specialized in Sri Lankan transit - ask me about routes, buses, trains, the app features, or getting around Sri Lanka!
- DO NOT answer questions about programming, technology (like React, Python, etc.), or topics unrelated to transit
- DO NOT make up information or use your general knowledge if it is not in the context

Guidelines:
- Speak directly to the user (you and your instead of formal language)
- Break information into easy-to-read points when listing things
- Give practical, real-world advice that is easy to follow
- Be encouraging and positive
- Always stay focused on Sri Lankan transit topics

Remember: You are a TRANSIT EXPERT for Sri Lanka, not a general-purpose AI. Stay in your lane!"""

        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            temperature=0.5,  # Higher temperature for more natural,friendly conversational responses
            google_api_key=settings.GOOGLE_GEMINI_API_KEY
        )

        # Create custom prompt template for user-friendly responses
        from langchain.prompts import PromptTemplate

        friendly_template = """You are Smart Transit Companion, a friendly AI travel buddy for Sri Lankan public transport!

CRITICAL INSTRUCTIONS:
1. You can ONLY answer questions about Sri Lankan public transportation and the Smart Transit Companion app
2. You must ONLY use information from the context provided below - DO NOT use your general knowledge
3. If the context does not contain the answer, say: I do not have that information in my transit knowledge base. I specialize in Sri Lankan buses, trains, routes, and the Smart Transit app. Ask me about those topics!
4. DO NOT answer questions about programming, technology, or non-transit topics
5. If someone asks about React, Python, coding, etc., respond: I am a transit assistant, not a tech tutor! Ask me about Sri Lankan transportation instead!

Context from Sri Lankan transit knowledge base:
{context}

User Question: {question}

Your Answer (2-4 sentences, ONLY based on the context above, stay friendly and helpful):"""

        FRIENDLY_PROMPT = PromptTemplate(
            template=friendly_template, input_variables=["context", "question"]
        )

        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": FRIENDLY_PROMPT},
            return_source_documents=True  # ✅ Return source docs for debugging
        )
        
        print("✅ RAG system initialized successfully!")
        print(f"   📚 Vector DB: {db_path}")
        print(f"   📄 Documents: {len(chunks)} chunks")
        print(f"   🔍 Retriever: k=3 (retrieves top 3 relevant documents)")
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {str(e)}")
        vectordb = None
        qa_chain = None

@router.get("/")
async def root():
    return {"message": "RAG QA System is running!", "status": "healthy"}

@router.post("/ask", response_model=IntentResponse)
async def ask_question(request: QuestionRequest):
    global qa_chain
    
    if qa_chain is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        from app.services.cache_manager import chatbot_cache
        
        print(f"Processing question with intent detection: {request.question}")
        
        # ✅ Await the async intent detection function
        intent_data = await detect_intent_and_extract_params(request.question)
        intent_type = intent_data.get("intent_type", "general_info")
        extracted_params = intent_data.get("extracted_params", {})
        
        print(f"Detected intent: {intent_type} with params: {extracted_params}")
        
        if intent_type == "route_planning":
            return await handle_route_planning_intent(request, extracted_params)
        elif intent_type == "saved_routes":
            return await handle_saved_routes_intent(request)
        elif intent_type == "disruptions":
            return await handle_disruptions_intent(request)
        else:
            return await handle_general_info_intent(request, qa_chain, tracer, langsmith_client, chatbot_cache)
        
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

async def handle_route_planning_intent(request: QuestionRequest, extracted_params: Dict[str, Any]) -> IntentResponse:
    try:
        print(f"Handling route planning intent for: {request.question}")
        source = extracted_params.get("source")
        destination = extracted_params.get("destination")
        mode = extracted_params.get("mode") or "transit"  # Ensure mode is never None
        preferred_transit = extracted_params.get("preferred_transit")
        
        if not source or not destination:
            return IntentResponse(
                question=request.question,
                answer="I'd be happy to help plan a route! Could you please specify your start and end locations?",
                intent_type="general_info",
                requires_action=False
            )
        
        if not request.user_id:
            return IntentResponse(
                question=request.question,
                answer=f"I can help you plan a route from {source} to {destination}. However, you'll need to be logged in for this feature.",
                intent_type="route_planning",
                requires_action=False
            )
        
        route_result = await call_plan_route_endpoint(
            user_id=request.user_id,
            source=source,
            destination=destination,
            mode=mode,
            preferred_transit=preferred_transit
        )
        
        print(f"Route result: {route_result}")
        print(f"Route result status: {route_result.get('status')}")
        
        if route_result.get("status") == "success":
            # Auto-save best route logic
            try:
                response_payload = route_result.get("response", {})
                request_id = response_payload.get("request_id") or f"req_{datetime.utcnow().timestamp()}"
                best_route = response_payload.get("best_route") or (response_payload.get("all_routes", [None])[0])
                
                if best_route:
                    route_id = best_route.get("route_id") or request_id
                    route_document = {
                        "user_id": request.user_id, "route_id": route_id, "source": source, "destination": destination,
                        "route_data": best_route, "created_at": datetime.utcnow(),
                        "metadata": {"saved_via": "chatbot_auto", "mode": mode, "request_id": request_id},
                        "saved_at": datetime.utcnow()
                    }
                    
                    # Save to route_history collection (existing behavior)
                    await db.database.route_history.insert_one(route_document)
                    await db.database.user_preferences.update_one(
                        {"user_id": request.user_id},
                        {"$push": {"route_history": {"$each": [route_document], "$slice": -50}}, "$set": {"updated_at": datetime.utcnow()}},
                        upsert=True
                    )
                    
                    # FIX: Also save to travel_requests collection so mobile app can find it
                    travel_request_document = {
                        "user_id": request.user_id,
                        "source": source,
                        "destination": destination,
                        "mode": mode,
                        "preferred_transit": None,
                        "departure_time": None,
                        "request_timestamp": datetime.utcnow(),
                        "result": route_result  # Store the complete result from the travel agent
                    }
                    await db.database.travel_requests.insert_one(travel_request_document)
                    print(f"Chatbot: Saved route to both route_history and travel_requests collections")
                    
            except Exception as save_err:
                print(f"Error auto-saving route: {save_err}")

            return IntentResponse(
                question=request.question,
                answer=f"🚀 I've planned your route from {source} to {destination}! The AI agents found the best options for you.",
                intent_type="route_planning",
                # FIX: send the full result so mobile can read .response.*
                action_data={"result": route_result, "source": source, "destination": destination, "mode": mode},
                requires_action=True
            )
        else:
            return IntentResponse(
                question=request.question,
                answer=f"I had an issue planning your route from {source} to {destination}. Please try again.",
                intent_type="route_planning",
                requires_action=False
            )
            
    except Exception as e:
        print(f"Error in route planning intent: {str(e)}")
        import traceback
        traceback.print_exc()
        return IntentResponse(question=request.question, answer="I'm having trouble processing your route request. Please try again later.", intent_type="general_info", requires_action=False)

async def handle_saved_routes_intent(request: QuestionRequest) -> IntentResponse:
    return IntentResponse(
        question=request.question,
        answer="📋 I can show you your saved routes and route history.",
        intent_type="saved_routes",
        action_data={"action": "view_saved_routes"},
        requires_action=True
    )

async def handle_disruptions_intent(request: QuestionRequest) -> IntentResponse:
    return IntentResponse(
        question=request.question,
        answer="⚠️ I can check for current disruptions, delays, and traffic issues.",
        intent_type="disruptions",
        action_data={"action": "view_disruptions"},
        requires_action=True
    )

async def handle_general_info_intent(request: QuestionRequest, qa_chain, tracer, langsmith_client, chatbot_cache) -> IntentResponse:
    try:
        print(f"🔍 RAG: Starting RAG retrieval for question: {request.question}")
        
        cache_key = {"question": request.question, "temperature": request.temperature}
        cached_response = chatbot_cache.get(cache_key)
        if cached_response:
            print(f"📦 RAG: Returning cached response for: {request.question[:50]}...")
            return IntentResponse(
                question=request.question, 
                answer=cached_response["answer"], 
                intent_type="general_info", 
                requires_action=False,
                action_data={"rag_used": True, "from_cache": True}
            )
        
        print(f"🔄 RAG: No cache found, performing vector search...")
        
        max_retries = 3
        retrieved_docs = []
        for attempt in range(max_retries):
            try:
                if request.temperature != 0.5:
                    # Create new QA chain with custom temperature and friendly prompt
                    print(f"🔧 RAG: Creating custom QA chain with temperature={request.temperature}")
                    from langchain.prompts import PromptTemplate

                    friendly_template = """You are Smart Transit Companion, a friendly AI travel buddy for Sri Lankan public transport!

CRITICAL INSTRUCTIONS:
1. You can ONLY answer questions about Sri Lankan public transportation and the Smart Transit Companion app
2. You must ONLY use information from the context provided below - DO NOT use your general knowledge
3. If the context does not contain the answer, say: I do not have that information in my transit knowledge base. I specialize in Sri Lankan buses, trains, routes, and the Smart Transit app. Ask me about those topics!
4. DO NOT answer questions about programming, technology, or non-transit topics
5. If someone asks about React, Python, coding, etc., respond: I am a transit assistant, not a tech tutor! Ask me about Sri Lankan transportation instead!

Context from Sri Lankan transit knowledge base:
{context}

User Question: {question}

Your Answer (2-4 sentences, ONLY based on the context above, stay friendly and helpful):"""

                    FRIENDLY_PROMPT = PromptTemplate(
                        template=friendly_template, input_variables=["context", "question"]
                    )

                    llm = ChatGoogleGenerativeAI(
                        model="gemini-flash-lite-latest",
                        temperature=request.temperature,
                        google_api_key=settings.GOOGLE_GEMINI_API_KEY
                    )
                    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
                    qa_chain = RetrievalQA.from_chain_type(
                        llm,
                        retriever=retriever,
                        chain_type_kwargs={"prompt": FRIENDLY_PROMPT},
                        return_source_documents=True  # ✅ Return source docs for logging
                    )
                
                print(f"📚 RAG: Invoking RAG chain to retrieve from knowledge base...")
                
                # ✅ Use 'ainvoke' for non-blocking call
                if tracer:
                    result = await qa_chain.ainvoke({"query": request.question}, config={"callbacks": [tracer], "tags": ["rag-question"], "metadata": {"temperature": request.temperature}})
                else:
                    result = await qa_chain.ainvoke({"query": request.question})
                
                # ✅ Extract retrieved documents if available
                if "source_documents" in result:
                    retrieved_docs = result["source_documents"]
                    print(f"✅ RAG: Retrieved {len(retrieved_docs)} documents from vector database")
                    for i, doc in enumerate(retrieved_docs[:2]):  # Log first 2 docs
                        print(f"  📄 Doc {i+1}: {doc.page_content[:100]}...")
                else:
                    print(f"⚠️ RAG: No source documents returned (might be using default chain)")
                
                break
                
            except Exception as quota_error:
                error_str = str(quota_error)
                if "quota" in error_str.lower() or "429" in error_str:
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Quota exceeded, retrying in {delay:.1f}s")
                        # ✅ Use 'asyncio.sleep' for non-blocking sleep
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return IntentResponse(question=request.question, answer="I'm currently experiencing high demand. Please try again in a few minutes.", intent_type="general_info", requires_action=False)
                else:
                    raise quota_error
            
        answer = result["result"]
        print(f"✅ RAG: Generated answer from knowledge base")
        print(f"  ❓ Question: {request.question}")
        print(f"  💬 Answer: {answer[:200]}...")
        
        chatbot_cache.set(cache_key, {"answer": answer})
        
        if langsmith_client:
            try:
                langsmith_client.create_run(name="rag_question_answering", inputs={"question": request.question, "temperature": request.temperature}, outputs={"answer": answer}, run_type="chain")
            except Exception as ls_error:
                print(f"LangSmith logging error: {ls_error}")
        
        # ✅ Return with RAG metadata
        return IntentResponse(
            question=request.question, 
            answer=answer, 
            intent_type="general_info", 
            requires_action=False,
            action_data={
                "rag_used": True,
                "documents_retrieved": len(retrieved_docs),
                "knowledge_source": "transit_guide"
            }
        )
        
    except Exception as e:
        print(f"Error in general info intent: {str(e)}")
        import traceback
        traceback.print_exc()
        return IntentResponse(question=request.question, answer="I'm having trouble processing your question. Please try rephrasing it.", intent_type="general_info", requires_action=False)

@router.get("/health")
async def health_check():
    db_path = Path(__file__).parent / "db"
    return {
        "status": "healthy", 
        "rag_system_initialized": qa_chain is not None, 
        "vector_db_exists": db_path.exists(), 
        "langsmith_enabled": langsmith_client is not None,
        "vector_db_path": str(db_path)
    }

@router.post("/reinitialize")
async def reinitialize_system():
    try:
        initialize_rag_system()
        return {"message": "RAG system reinitialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reinitializing system: {str(e)}")

@router.post("/debug-rag")
async def debug_rag(question: str):
    """
    Debug endpoint to test RAG system with detailed output
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 DEBUG RAG TEST")
        print(f"{'='*60}")
        print(f"Question: {question}\n")
        
        # Test intent detection
        intent_data = await detect_intent_and_extract_params(question)
        print(f"\n📊 Intent Detection Result:")
        print(f"   Intent: {intent_data.get('intent_type')}")
        print(f"   Params: {intent_data.get('extracted_params')}")
        
        # Test RAG retrieval
        if qa_chain and vectordb:
            print(f"\n📚 Testing RAG Retrieval...")
            retriever = vectordb.as_retriever(search_kwargs={"k": 3})
            docs = await retriever.ainvoke(question)
            
            print(f"   Retrieved {len(docs)} documents:")
            for i, doc in enumerate(docs):
                print(f"\n   Doc {i+1}:")
                print(f"   {doc.page_content[:200]}...")
            
            # Test full QA chain
            print(f"\n🤖 Testing Full QA Chain...")
            result = await qa_chain.ainvoke({"query": question})
            
            return {
                "status": "success",
                "question": question,
                "intent_detection": intent_data,
                "documents_retrieved": len(docs),
                "documents": [{"content": doc.page_content[:200], "metadata": doc.metadata} for doc in docs],
                "qa_result": result.get("result"),
                "source_documents_in_result": len(result.get("source_documents", [])),
                "rag_working": True
            }
        else:
            return {
                "status": "error",
                "message": "RAG system not initialized",
                "qa_chain_initialized": qa_chain is not None,
                "vectordb_initialized": vectordb is not None
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/test-rag")
async def test_rag():
    """
    Quick test endpoint with predefined questions
    """
    test_questions = [
        "What is Smart Transit Companion?",
        "How do I use the app?",
        "What features does the app have?",
        "Tell me about AI agents",
    ]
    
    results = []
    for question in test_questions:
        try:
            intent_data = await detect_intent_and_extract_params(question)
            results.append({
                "question": question,
                "intent": intent_data.get("intent_type"),
                "should_use_rag": intent_data.get("intent_type") == "general_info",
                "status": "✅ Will use RAG" if intent_data.get("intent_type") == "general_info" else "❌ Will NOT use RAG"
            })
        except Exception as e:
            results.append({
                "question": question,
                "error": str(e),
                "status": "❌ Error"
            })
    
    return {
        "test_results": results,
        "rag_initialized": qa_chain is not None,
        "summary": f"{sum(1 for r in results if r.get('should_use_rag'))} out of {len(results)} questions will use RAG"
    }

# ✅ Make the function async
async def detect_intent_and_extract_params(question: str) -> Dict[str, Any]:
    try:
        print(f"🎯 INTENT: Detecting intent for: {question}")
        
        intent_llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0.1, google_api_key=settings.GOOGLE_GEMINI_API_KEY, convert_system_message_to_human=True)
        
        intent_prompt = f"""You are an intent classifier for a Sri Lankan public transit assistant chatbot.

Analyze the user question and classify it into ONE of these intents:

1. route_planning - ONLY when user explicitly asks to plan/find a route, get directions, or travel from A to B
   Examples: How do I get from Colombo to Kandy, Plan a route to the airport, Directions to Galle
   
2. saved_routes - When user asks about their saved routes or route history
   Examples: Show my saved routes, My route history, What routes did I save
   
3. disruptions - When user asks about traffic, delays, or disruptions
   Examples: Any delays today, Traffic conditions, Are there disruptions
   
4. general_info - For ALL other questions about transit, fares, how to use services, general knowledge
   Examples: What is react, How do buses work, What are the fares, Tell me about trains, How to use the app

IMPORTANT RULES:
- If unsure, choose general_info (this uses the knowledge base)
- Only use route_planning if the question clearly asks for route directions between two locations
- Questions about general transit information should be general_info, NOT route_planning

Question: {question}

Return ONLY a JSON object with intent_type and extracted_params.
Example for general: {{"intent_type": "general_info", "extracted_params": {{}}}}
Example for route: {{"intent_type": "route_planning", "extracted_params": {{"source": "Colombo", "destination": "Kandy", "mode": "transit"}}}}"""
        
        # ✅ Use the async 'ainvoke' method
        response = await intent_llm.ainvoke(intent_prompt)
        result_text = response.content.strip().replace('```json', '').replace('```', '').strip()
        
        print(f"🤖 INTENT: Raw LLM response: {result_text}")
        
        try:
            intent_data = json.loads(result_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            intent_data = json.loads(json_match.group()) if json_match else {"intent_type": "general_info", "extracted_params": {}}
        
        detected_intent = intent_data.get("intent_type", "general_info")
        print(f"✅ INTENT: Detected intent = '{detected_intent}'")
        
        # Ensure mode is never None for route planning
        if detected_intent == "route_planning":
            extracted_params = intent_data.get("extracted_params", {})
            if extracted_params.get("mode") is None:
                extracted_params["mode"] = "transit"
            print(f"📍 INTENT: Route params - source: {extracted_params.get('source')}, dest: {extracted_params.get('destination')}, mode: {extracted_params.get('mode')}")
        
        return intent_data
        
    except Exception as e:
        print(f"❌ INTENT: Error in intent detection: {str(e)}")
        print(f"⚠️ INTENT: Defaulting to 'general_info' (will use RAG)")
        return {"intent_type": "general_info", "extracted_params": {}}

# ✅ Make the function async and assume run_travel_agent is also async
async def call_plan_route_endpoint(user_id: str, source: str, destination: str, mode: str = "transit", preferred_transit: Optional[str] = None) -> Dict[str, Any]:
    try:
        from app.services.workflow import run_travel_agent
        
        print(f"Calling plan-route for {source} to {destination} ({mode})")
        
        # ✅ Await the travel agent workflow
        result = await run_travel_agent(
            source=source,
            destination=destination,
            mode=mode,
            user_id=user_id,
            preferred_transit=preferred_transit
        )
        
        return result
        
    except Exception as e:
        print(f"Error calling plan-route: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e), "message": "Failed to plan route"}

initialize_rag_system()