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
    user_id: Optional[str] = None

class QuestionResponse(BaseModel):
    question: str
    answer: str

class IntentResponse(BaseModel):
    question: str
    answer: str
    intent_type: str  # 'route_planning', 'saved_routes', 'disruptions', 'general_info'
    action_data: Optional[Dict[str, Any]] = None  # Contains extracted params or API response
    requires_action: bool = False  # If true, frontend should show action button

def initialize_rag_system():
    """Initialize the RAG system components"""
    global vectordb, qa_chain
    
    try:
        # Check if chromadb is available
        try:
            import chromadb
        except ImportError:
            print("WARNING: chromadb not installed. Chatbot will be disabled.")
            print("To enable chatbot: pip install chromadb")
            vectordb = None
            qa_chain = None
            return
        
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
            google_api_key=settings.GOOGLE_GEMINI_API_KEY
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
        
        # LLM - Using latest Gemini 2.0 Flash (faster, better, cheaper)
        system_prompt = """You are Smart Transit Companion, an AI assistant specialized in Sri Lankan public transportation. 

        Your role:
        - Help users navigate buses, trains, tuk-tuks, and other transport modes in Sri Lanka
        - Provide accurate, up-to-date information about routes, schedules, and fares
        - Answer questions in a friendly, helpful manner
        - Support multiple languages (Sinhala, Tamil, English)
        - Focus on practical, actionable advice for travelers

        Guidelines:
        - Always be concise and practical
        - Include specific route numbers, bus stops, and landmarks when available
        - Mention alternative transport options when relevant
        - Be culturally aware of Sri Lankan transportation customs
        - If you don't have specific information, suggest how users can find it

        Remember: You're helping people navigate Sri Lanka's public transport system efficiently and safely."""

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", 
            temperature=0.2,
            google_api_key=settings.GOOGLE_GEMINI_API_KEY,
            convert_system_message_to_human=True,
            system_message=system_prompt
        )
        
        # Retrieval QA Chain with limited results
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})  # Limit to 3 results
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        
        print("RAG system initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing RAG system: {str(e)}")
        print("WARNING: Chatbot will be disabled. Install chromadb with: pip install chromadb")
        # Don't raise error, just disable chatbot
        vectordb = None
        qa_chain = None

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG QA System is running!", "status": "healthy"}

@router.post("/ask", response_model=IntentResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question with intent detection and appropriate action handling
    """
    global qa_chain
    
    if qa_chain is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        import time
        import random
        from app.services.cache_manager import chatbot_cache
        
        print(f"Processing question with intent detection: {request.question}")
        
        # Step 1: Detect intent and extract parameters
        intent_data = detect_intent_and_extract_params(request.question)
        intent_type = intent_data.get("intent_type", "general_info")
        extracted_params = intent_data.get("extracted_params", {})
        
        print(f"Detected intent: {intent_type} with params: {extracted_params}")
        
        # Step 2: Handle different intents
        if intent_type == "route_planning":
            return await handle_route_planning_intent(request, extracted_params)
        elif intent_type == "saved_routes":
            return await handle_saved_routes_intent(request)
        elif intent_type == "disruptions":
            return await handle_disruptions_intent(request)
        else:
            # Handle general info with RAG
            return await handle_general_info_intent(request, qa_chain, tracer, langsmith_client, chatbot_cache)
        
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

async def handle_route_planning_intent(request: QuestionRequest, extracted_params: Dict[str, Any]) -> IntentResponse:
    """
    Handle route planning intent by calling the plan-route endpoint
    """
    try:
        source = extracted_params.get("source")
        destination = extracted_params.get("destination")
        mode = extracted_params.get("mode", "transit")
        preferred_transit = extracted_params.get("preferred_transit")
        
        if not source or not destination:
            # If we couldn't extract source/destination, fall back to RAG
            return IntentResponse(
                question=request.question,
                answer="I'd be happy to help you plan a route! Could you please specify where you want to go from and to? For example, 'I want to go from Colombo to Kandy'.",
                intent_type="general_info",
                requires_action=False
            )
        
        # Check if user_id is provided
        if not request.user_id:
            return IntentResponse(
                question=request.question,
                answer="I can help you plan a route from {source} to {destination}. However, you'll need to be logged in to use the route planning feature.",
                intent_type="route_planning",
                requires_action=False
            )
        
        # Call the plan-route endpoint
        route_result = await call_plan_route_endpoint(
            user_id=request.user_id,
            source=source,
            destination=destination,
            mode=mode,
            preferred_transit=preferred_transit
        )
        
        if route_result["success"]:
            # Auto-save best route to history (equivalent to POST /api/v1/travel/save-route)
            try:
                planned = route_result.get("data", {})
                response_payload = planned.get("response", {}) if isinstance(planned, dict) else {}
                request_id = response_payload.get("request_id") or f"req_{datetime.utcnow().timestamp()}"

                # Choose best route or fallback to first available
                best_route = response_payload.get("best_route")
                routes = []
                if not best_route:
                    if response_payload.get("recommended_routes"):
                        routes = response_payload.get("recommended_routes", [])
                        # recommended_routes may be list of {route: {...}, score: ...}
                        if routes:
                            candidate = routes[0]
                            best_route = candidate.get("route") if isinstance(candidate, dict) and "route" in candidate else candidate
                    elif response_payload.get("all_routes"):
                        routes = response_payload.get("all_routes", [])
                        if routes:
                            best_route = routes[0]
                    elif response_payload.get("routes"):
                        routes = response_payload.get("routes", [])
                        if routes:
                            best_route = routes[0]

                if best_route:
                    route_id = best_route.get("route_id") or request_id
                    route_document = {
                        "user_id": request.user_id,
                        "route_id": route_id,
                        "source": source,
                        "destination": destination,
                        "route_data": best_route,
                        "created_at": datetime.utcnow(),
                        "metadata": {
                            "saved_via": "chatbot_auto",
                            "mode": mode,
                            "request_id": request_id
                        },
                        "saved_at": datetime.utcnow()
                    }

                    # Insert into route_history
                    await db.database.route_history.insert_one(route_document)

                    # Mirror save-route endpoint behavior: update user_preferences route_history (keep last 50)
                    await db.database.user_preferences.update_one(
                        {"user_id": request.user_id},
                        {
                            "$push": {
                                "route_history": {"$each": [route_document], "$slice": -50}
                            },
                            "$set": {"updated_at": datetime.utcnow()}
                        },
                        upsert=True
                    )
            except Exception as save_err:
                # Log auto-save errors but don't fail the main response
                try:
                    await db.database.error_logs.insert_one({
                        "timestamp": datetime.utcnow(),
                        "user_id": request.user_id,
                        "endpoint": "chatbot_auto_save_route",
                        "error": str(save_err),
                        "request_data": {
                            "source": source,
                            "destination": destination,
                            "mode": mode
                        }
                    })
                except Exception:
                    pass
            return IntentResponse(
                question=request.question,
                answer=f"🚀 I've planned your route from {source} to {destination}! The AI agents have analyzed multiple options and found the best routes for you.",
                intent_type="route_planning",
                action_data={
                    "route_result": route_result["data"],
                    "source": source,
                    "destination": destination,
                    "mode": mode
                },
                requires_action=True
            )
        else:
            return IntentResponse(
                question=request.question,
                answer=f"I encountered an issue planning your route from {source} to {destination}. Please try again or contact support if the problem persists.",
                intent_type="route_planning",
                requires_action=False
            )
            
    except Exception as e:
        print(f"Error in route planning intent: {str(e)}")
        return IntentResponse(
            question=request.question,
            answer="I'm having trouble processing your route request. Please try rephrasing your question or try again later.",
            intent_type="general_info",
            requires_action=False
        )

async def handle_saved_routes_intent(request: QuestionRequest) -> IntentResponse:
    """
    Handle saved routes intent
    """
    return IntentResponse(
        question=request.question,
        answer="📋 I can help you view your saved routes and route history. This will show you all the routes you've planned and saved.",
        intent_type="saved_routes",
        action_data={"action": "view_saved_routes"},
        requires_action=True
    )

async def handle_disruptions_intent(request: QuestionRequest) -> IntentResponse:
    """
    Handle disruptions intent
    """
    return IntentResponse(
        question=request.question,
        answer="⚠️ I can check for current disruptions, delays, and traffic issues that might affect your travel. This includes real-time updates from our community and official sources.",
        intent_type="disruptions",
        action_data={"action": "view_disruptions"},
        requires_action=True
    )

async def handle_general_info_intent(request: QuestionRequest, qa_chain, tracer, langsmith_client, chatbot_cache) -> IntentResponse:
    """
    Handle general information requests using the RAG system
    """
    try:
        import time
        import random
        
        # Check cache first to avoid API calls
        cache_key = {"question": request.question, "temperature": request.temperature}
        cached_response = chatbot_cache.get(cache_key)
        if cached_response:
            print(f"Returning cached response for: {request.question[:50]}...")
            return IntentResponse(
                question=request.question, 
                answer=cached_response["answer"],
                intent_type="general_info",
                requires_action=False
            )
        
        # Add exponential backoff for quota limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Update LLM temperature if different from default
                if request.temperature != 0.2:
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash-exp", 
                        temperature=request.temperature,
                        google_api_key=settings.GOOGLE_GEMINI_API_KEY,
                        convert_system_message_to_human=True
                    )
                    retriever = vectordb.as_retriever(search_kwargs={"k": 1})  # Reduce to 1 result to save quota
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
                
                # If successful, break out of retry loop
                break
                
            except Exception as quota_error:
                error_str = str(quota_error)
                if "quota" in error_str.lower() or "429" in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff: 2^attempt seconds + random jitter
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Quota exceeded, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        # Final attempt failed, return fallback response
                        return IntentResponse(
                            question=request.question, 
                            answer="I'm currently experiencing high demand. The Smart Transit Companion app helps you navigate Sri Lankan public transport with real-time information, route planning, and multi-language support. Please try again in a few minutes.",
                            intent_type="general_info",
                            requires_action=False
                        )
                else:
                    # Non-quota error, re-raise
                    raise quota_error
            
        answer = result["result"]
        print(f"Question: {request.question}\nAnswer: {answer}")
        
        # Cache the successful response
        chatbot_cache.set(cache_key, {"answer": answer})
        
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
        
        return IntentResponse(
            question=request.question, 
            answer=answer,
            intent_type="general_info",
            requires_action=False
        )
        
    except Exception as e:
        print(f"Error in general info intent: {str(e)}")
        return IntentResponse(
            question=request.question,
            answer="I'm having trouble processing your question. Please try rephrasing it or try again later.",
            intent_type="general_info",
            requires_action=False
        )

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

def detect_intent_and_extract_params(question: str) -> Dict[str, Any]:
    """
    Use LLM to detect user intent and extract relevant parameters
    """
    try:
        # Create a separate LLM instance for intent detection
        intent_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", 
            temperature=0.1,
            google_api_key=settings.GOOGLE_GEMINI_API_KEY,
            convert_system_message_to_human=True,
        )
        
        intent_prompt = f"""
        Analyze the following user question about Sri Lankan transportation and classify the intent.
        
        Question: "{question}"
        
        Classify the intent as one of these types:
        1. "route_planning" - User wants to plan a route from one place to another
        2. "saved_routes" - User wants to see their saved routes or route history
        3. "disruptions" - User wants to check for delays, disruptions, or traffic issues
        4. "general_info" - General questions about transportation, fares, schedules, etc.
        
        If the intent is "route_planning", also extract:
        - source: The starting location
        - destination: The ending location
        - mode: Preferred travel mode if mentioned (transit, driving, train, bus, etc.)
        
        Return ONLY a JSON object in this exact format:
        {{
            "intent_type": "one of the four types above",
            "confidence": 0.95,
            "extracted_params": {{
                "source": "extracted source location or null",
                "destination": "extracted destination location or null", 
                "mode": "extracted mode or 'transit'",
                "preferred_transit": "specific transit preference or null"
            }}
        }}
        """
        
        response = intent_llm.invoke(intent_prompt)
        result_text = response.content.strip()
        
        # Clean up the response to ensure it's valid JSON
        if result_text.startswith('```json'):
            result_text = result_text.replace('```json', '').replace('```', '').strip()
        elif result_text.startswith('```'):
            result_text = result_text.replace('```', '').strip()
        
        # Parse the JSON response
        try:
            intent_data = json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group())
            else:
                # Ultimate fallback
                intent_data = {
                    "intent_type": "general_info",
                    "confidence": 0.5,
                    "extracted_params": {
                        "source": None,
                        "destination": None,
                        "mode": "transit",
                        "preferred_transit": None
                    }
                }
        
        return intent_data
        
    except Exception as e:
        print(f"Error in intent detection: {str(e)}")
        # Fallback to general info
        return {
            "intent_type": "general_info",
            "confidence": 0.5,
            "extracted_params": {
                "source": None,
                "destination": None,
                "mode": "transit",
                "preferred_transit": None
            }
        }

async def call_plan_route_endpoint(user_id: str, source: str, destination: str, mode: str = "transit", preferred_transit: str = None) -> Dict[str, Any]:
    """
    Call the plan-route endpoint when route planning intent is detected
    """
    try:
        from app.services.workflow import run_travel_agent
        
        print(f"Calling plan-route for {source} to {destination} ({mode})")
        
        # Call the travel agent workflow directly
        result = run_travel_agent(
            source=source,
            destination=destination,
            mode=mode,
            user_id=user_id,
            preferred_transit=preferred_transit
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Route planning completed for {source} to {destination}"
        }
        
    except Exception as e:
        print(f"Error calling plan-route: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to plan route"
        }

# Initialize the RAG system when the module is loaded
initialize_rag_system()