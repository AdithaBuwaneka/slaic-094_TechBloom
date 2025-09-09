# Transit Companion Backend

A FastAPI backend application with MongoDB database integration for the Transit Companion app.

## Features

- **🚀 FastAPI Backend**: Modern async web framework with automatic API documentation
- **🗄️ MongoDB Atlas Integration**: Cloud database with Motor async driver
- **🤖 RAG Chatbot System**: Intelligent Q&A using ChromaDB vector database and Google Gemini
- **🧠 Multi-Agent Travel Planning**: AI-powered route optimization with specialized agents
- **🛣️ Google Maps Integration**: Real-time routing and directions
- **📊 Disruption Monitoring**: Active traffic and transit disruption tracking
- **👤 User Preference Learning**: Personalized route recommendations
- **🔍 Web Search Integration**: Real-time information gathering (optional)
- **📈 LLM Observability**: Langfuse integration for AI performance monitoring
- **⚡ Health Monitoring**: Comprehensive health checks and database status
- **🌐 CORS Enabled**: Frontend-ready with cross-origin support
- **📝 Auto-Documentation**: Swagger UI and ReDoc API documentation
- **🔧 Environment-based Configuration**: Secure .env file management

## Project Structure

```
BACKEND/
├── app/
│   ├── api/
│   │   ├── routes.py          # Main API endpoints and routing
│   │   ├── v1/
│   │   │   ├── travel_routes.py    # Multi-agent travel planning APIs
│   │   │   ├── chatbot_routes.py   # Chatbot routing wrapper
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # MongoDB connection & setup
│   │   └── __init__.py
│   ├── services/
│   │   ├── workflow.py        # Multi-agent workflow orchestration
│   │   ├── agent_nodes.py     # Individual AI agent implementations
│   │   ├── tool_functions.py  # External API integrations (Google Maps, Serper)
│   │   ├── analysis_tools.py  # Data analysis and optimization tools
│   │   ├── llm_summarizer.py  # LLM summarization service
│   │   ├── intelligent_disruption_service.py  # Smart disruption monitoring
│   │   ├── langfuse_service.py # Observability and tracing service
│   │   ├── google_maps_service.py # Google Maps API wrapper
│   │   └── main_runner.py     # CLI execution entry point
│   ├── models/
│   │   ├── travel_schema.py   # Travel planning data models
│   │   └── path.py           # Route and path models
│   ├── chatbot/
│   │   ├── chatbot.py        # RAG chatbot implementation
│   │   ├── transit_app_guide.txt # Knowledge base document
│   │   └── db/               # ChromaDB vector database
│   ├── main.py               # FastAPI app initialization
│   └── __init__.py
├── .env                      # Environment variables (not in git)
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── run.py                   # Development server runner
└── README.md                # This file
```

## Setup

### Prerequisites

- **Python 3.9+** (tested with Python 3.13)
- **MongoDB Atlas** (cloud database) or local MongoDB instance
- **Google Maps API Key** (required for routing)
- **Google AI API Key** (required for Gemini LLM)
- **Optional**: Serper API Key (for web search functionality)
- **Optional**: Langfuse account (for LLM observability and tracing)

### Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd BACKEND
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Key packages installed:**
   - `fastapi` - Modern web framework
   - `motor` & `pymongo` - MongoDB async drivers
   - `langchain` & `langchain-community` - LLM framework
   - `chromadb` - Vector database for RAG
   - `google-generativeai` - Google Gemini AI
   - `uvicorn` - ASGI server

5. Set up environment variables:
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```
   
   Edit `.env` file with your configuration:
   ```bash
   # Application Settings
   APP_NAME=Transit Companion Backend
   DEBUG=true
   API_V1_STR=/api/v1
   
   # MongoDB Configuration (Atlas cloud database)
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=transit_companion_db
   
   # Security
   SECRET_KEY=your-secret-key-here-change-in-production
   BACKEND_CORS_ORIGINS=["*"]
   
   # Required API Keys
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   GOOGLE_API_KEY=your_google_api_key
   
   # Optional API Keys (leave empty if not using)
   SERPER_API_KEY=your_serper_api_key
   LANGCHAIN_API_KEY=your_langchain_api_key
   
   # Optional - Langfuse Configuration (LLM Observability)
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
   
   **Important Notes:**
   - MongoDB Atlas connection string format: `mongodb+srv://username:password@cluster.mongodb.net/`
   - Backend will run without SERPER_API_KEY (web search disabled)
   - Backend will run without Langfuse keys (observability disabled)
   - GOOGLE_MAPS_API_KEY and GOOGLE_API_KEY are required for core functionality

### Running the Application

#### Development Mode

```bash
python run.py
```

Or use the Windows batch file:
```bash
start.bat
```

The API will be available at: `http://localhost:8000`

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Core System Endpoints

#### Welcome
- **GET** `/api/v1/`
  - Returns welcome message and backend information
  - Response:
    ```json
    {
      "message": "Welcome to Transit Companion Backend API",
      "app_name": "Transit Companion Backend",
      "version": "1.0.0",
      "status": "running"
    }
    ```

#### Health Check
- **GET** `/api/v1/health`
  - Returns application and database health status
  - Response (healthy):
    ```json
    {
      "status": "healthy",
      "database": "connected",
      "mongodb_url_configured": true,
      "database_name": "transit_companion_db"
    }
    ```

#### Database Connection
- **GET** `/api/v1/db-connection`
  - Returns detailed database connection status and collections info
  - Response (connected):
    ```json
    {
      "connection_status": "connected",
      "database_name": "transit_companion_db",
      "mongodb_url": "mongodb+srv://...",
      "collections_count": 17,
      "collections": ["transit_routes", "user_preferences", ...]
    }
    ```

### 🤖 Chatbot APIs

#### Chatbot Health Check
- **GET** `/api/v1/chatbot/chatbot/health`
  - Returns RAG system status
  - Response:
    ```json
    {
      "status": "healthy",
      "rag_system_initialized": true,
      "vector_db_exists": true,
      "langsmith_enabled": false
    }
    ```

#### Ask Question
- **POST** `/api/v1/chatbot/chatbot/ask`
  - Ask questions about transit and travel
  - Request body:
    ```json
    {
      "question": "How do I use public transport?",
      "temperature": 0.2
    }
    ```
  - Response:
    ```json
    {
      "question": "How do I use public transport?",
      "answer": "Based on the transit guide, you can use public transport by..."
    }
    ```

#### Reinitialize RAG System
- **POST** `/api/v1/chatbot/chatbot/reinitialize`
  - Reinitialize the RAG system (useful after document updates)

### 🚗 Travel Agent APIs

#### Plan Route
- **POST** `/api/v1/travel/plan-route`
  - Multi-agent travel planning with AI optimization
  - Request body:
    ```json
    {
      "user_id": "user123",
      "source": "Colombo",
      "destination": "Kandy",
      "mode": "driving",
      "preferred_transit": "bus",
      "departure_time": "2024-01-01T10:00:00"
    }
    ```
  - Travel modes: `driving`, `two_wheeler`, `transit`, `uber`

#### Active Disruptions
- **GET** `/api/v1/travel/active-disruptions`
  - Get real-time traffic and transit disruptions
  - Response:
    ```json
    {
      "active_disruptions_count": 1,
      "disruptions": [{
        "disruption_id": "disp_001",
        "disruption_type": "delay",
        "severity": "medium",
        "description": "Traffic congestion due to road construction",
        "location": {"lat": 6.9271, "lng": 79.8612}
      }]
    }
    ```

#### User Preferences
- **GET** `/api/v1/travel/user-preferences/{user_id}`
  - Get user's travel preferences and history

#### Report Disruption
- **POST** `/api/v1/travel/report-disruption`
  - Report new traffic or transit disruptions

### 🛣️ Legacy Route Planning

#### Shortest Path (Google Maps)
- **POST** `/api/v1/shortest-path`
  - Direct Google Maps API integration
  - Request body:
    ```json
    {
      "start": "Colombo",
      "end": "Kandy",
      "mode": "driving",
      "departure_time": "2024-01-01T10:00:00",
      "transit_mode_preference": "bus"
    }
    ```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Configuration

The application uses environment variables for configuration:

### Core Settings
- `APP_NAME`: Application name (default: Transit Companion Backend)
- `DEBUG`: Enable/disable debug mode (default: True)  
- `API_V1_STR`: API version prefix (default: /api/v1)
- `SECRET_KEY`: Secret key for security operations
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins - set to `["*"]` to allow any frontend URL

### Database Configuration
- `MONGODB_URL`: MongoDB connection string (format: `mongodb+srv://user:pass@cluster.mongodb.net/`)
- `DATABASE_NAME`: MongoDB database name (default: transit_companion_db)

### Required API Keys
- `GOOGLE_MAPS_API_KEY`: Google Maps API for routing and directions
- `GOOGLE_API_KEY`: Google AI API for Gemini LLM (chatbot and agent reasoning)

### Optional API Keys
- `SERPER_API_KEY`: Serper API for web search functionality (if empty, web search disabled)
- `LANGCHAIN_API_KEY`: LangChain API for enhanced LLM features (optional)

### Optional Observability
- `LANGFUSE_PUBLIC_KEY`: Langfuse public key for LLM tracing
- `LANGFUSE_SECRET_KEY`: Langfuse secret key for LLM tracing  
- `LANGFUSE_HOST`: Langfuse host URL (default: https://cloud.langfuse.com)

## Development

### Adding New Endpoints

1. Add new routes in `app/api/routes.py`
2. Import and include the router in `app/main.py`

### Database Operations

Currently, the backend provides basic MongoDB connectivity testing and collections listing. Motor (async MongoDB driver) is used for database connections. Database operations can be added by implementing MongoDB models and services.

## Testing

### Quick Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Test Welcome Endpoint
```bash
curl http://localhost:8000/api/v1/
```

### Test Database Connection
```bash
curl http://localhost:8000/api/v1/db-connection
```

### Test Chatbot
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/chatbot/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I use public transport?"}'
```

### Test Travel Agent
```bash
curl -X POST "http://localhost:8000/api/v1/travel/plan-route" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "source": "Colombo", "destination": "Kandy", "mode": "driving"}'
```

### Test Active Disruptions
```bash
curl http://localhost:8000/api/v1/travel/active-disruptions
```

### Access Interactive Documentation
Open in browser: `http://localhost:8000/docs`

## Troubleshooting

### Database Connection Issues

1. **MongoDB Server**: Verify MongoDB is running on the specified host and port
2. **Connection URL**: Check MONGODB_URL in `.env` file
3. **Database Name**: Ensure DATABASE_NAME is correctly configured
4. **Network**: Check firewall/network connectivity to MongoDB host
5. **Health Check**: Use `/api/v1/health` and `/api/v1/db-connection` endpoints to see specific error messages

### Common Error Messages

- `"motor not installed"` → Run `pip install motor pymongo`
- `"connection refused"` → MongoDB server not running or wrong host/port
- `"ServerSelectionTimeoutError"` → MongoDB server not accessible or firewall blocking connection

### Import Errors

Make sure you're in the correct directory and virtual environment is activated:
```bash
# Check current directory
pwd

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

## Current Status

### ✅ **Core System (Fully Operational)**
- **🚀 API Server**: Running on `http://localhost:8000`
- **🗄️ MongoDB Atlas**: Connected with 17 collections in `transit_companion_db`
- **⚡ Health Monitoring**: `/api/v1/health` and `/api/v1/db-connection`
- **🌐 CORS**: Enabled for all frontend origins
- **📝 API Documentation**: Swagger UI at `/docs`, ReDoc at `/redoc`

### ✅ **AI Features (Fully Operational)**
- **🤖 RAG Chatbot**: ChromaDB vector database initialized with transit guide
- **🧠 Multi-Agent Travel Planning**: LangGraph workflow with specialized agents
- **🛣️ Google Maps Integration**: Real-time routing and directions
- **📊 Disruption Monitoring**: Active traffic/transit disruption tracking
- **👤 User Preferences**: Learning and recommendation system

### ⚠️ **Optional Features (Configurable)**
- **🔍 Web Search**: Disabled (requires SERPER_API_KEY)
- **📈 LLM Observability**: Disabled (requires Langfuse keys)
- **🔗 LangChain Tracing**: Disabled (requires LANGCHAIN_API_KEY)

### 🎯 **API Endpoints Status**
- **Core APIs**: ✅ All operational
- **Chatbot APIs**: ✅ Q&A, health checks, reinitialize
- **Travel Agent APIs**: ✅ Route planning, disruptions, preferences
- **Legacy APIs**: ✅ Google Maps direct integration

### 🚀 **Production Ready**
Backend is fully operational with core functionality working. Optional features can be enabled by adding the respective API keys to the `.env` file.