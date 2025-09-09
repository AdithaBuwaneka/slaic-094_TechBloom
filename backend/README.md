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
- **🌤️ Weather Integration**: Real-time weather data and travel advice via OpenWeather API
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
│   │   ├── tool_functions.py  # External API integrations (Google Maps, Serper, Weather)
│   │   ├── analysis_tools.py  # Data analysis and optimization tools
│   │   ├── llm_summarizer.py  # LLM summarization service
│   │   ├── intelligent_disruption_service.py  # Smart disruption monitoring
│   │   ├── weather_service.py # OpenWeather API integration
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
- **OpenWeather API Key** (required for weather data and travel advice)
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
   OPENWEATHER_API_KEY=your_openweather_api_key
   
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
   - GOOGLE_MAPS_API_KEY, GOOGLE_API_KEY, and OPENWEATHER_API_KEY are required for core functionality

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

#### Plan Route (Multi-Agent AI)
- **POST** `/api/v1/travel/plan-route`
  - Advanced multi-agent travel planning with AI optimization
  - Uses 6 specialized agents: input_processing → mode_router → standard_route/transit_route_aggregation → route_optimization → disruption_monitoring → response_compilation
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
  - **Travel modes**: `driving`, `two_wheeler`, `transit`, `uber`
  - **Processing time**: 1-15 seconds (depending on mode complexity)
  - Response includes: optimized routes, recommendation scores, processing details, agent execution summary

#### Active Disruptions
- **GET** `/api/v1/travel/active-disruptions`
  - Get real-time traffic and transit disruptions
  - Uses intelligent disruption monitoring with Gemini AI
  - Response:
    ```json
    {
      "active_disruptions_count": 0,
      "disruptions": [],
      "monitoring_enabled": true,
      "last_check": "2025-09-10T03:40:00Z"
    }
    ```

#### User Preferences
- **GET** `/api/v1/travel/user-preferences/{user_id}`
  - Get user's travel preferences and learning history
  - Returns personalized settings for route optimization

#### Report Disruption
- **POST** `/api/v1/travel/report-disruption`
  - Report new traffic or transit disruptions
  - Integrates with AI disruption analysis system
  - Request body:
    ```json
    {
      "user_id": "user123",
      "route_id": "route_001",
      "location": "Colombo city center",
      "disruption_type": "traffic",
      "severity": "high",
      "description": "Heavy traffic due to construction",
      "affected_routes": ["route_001", "route_002"]
    }
    ```

### 🛣️ Legacy Route Planning

#### Shortest Path (Google Maps Direct)
- **POST** `/api/v1/shortest-path`
  - Direct Google Maps API integration (legacy endpoint)
  - Faster response but less intelligent than multi-agent planning
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
  - **Travel modes**: `driving`, `transit`, `walking`, `bicycling`, `three_wheeler`
  - **Response**: Detailed step-by-step directions with distance, duration, and instructions
  - **Processing time**: < 1 second
  - Example response:
    ```json
    {
      "origin": "Colombo, Sri Lanka",
      "destination": "Kandy, Sri Lanka",
      "distance_text": "145.9 km",
      "duration_text": "12569 seconds",
      "steps": [/* 29 detailed navigation steps */]
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

### Core System Health Checks

#### Test Welcome Endpoint
```bash
curl http://localhost:8000/api/v1/
# Expected: Welcome message with app info
```

#### Test Health Check
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", "database": "connected"}
```

#### Test Database Connection
```bash
curl http://localhost:8000/api/v1/db-connection
# Expected: Connection status + 17 collections list
```

### Weather API Testing

#### Test Weather Service Status
```bash
curl http://localhost:8000/api/v1/weather/
# Expected: Service status and available endpoints
```

#### Test Current Weather
```bash
curl http://localhost:8000/api/v1/weather/current/Colombo
# Expected: Real-time weather data for Colombo
```

#### Test Weather Forecast
```bash
curl http://localhost:8000/api/v1/weather/forecast/Kandy
# Expected: 40 forecast entries (5 days, 3-hour intervals)
```

#### Test Travel Weather Advice
```bash
curl http://localhost:8000/api/v1/weather/travel-advice/Colombo
# Expected: AI-generated travel advice based on weather
```

#### Test Weather by Coordinates
```bash
curl -X POST "http://localhost:8000/api/v1/weather/coordinates" \
  -H "Content-Type: application/json" \
  -d '{"lat": 6.9271, "lng": 79.8612}'
# Expected: Weather data for specific coordinates
```

### Chatbot API Testing

#### Test Chatbot Health
```bash
curl http://localhost:8000/api/v1/chatbot/ask
# Expected: RAG system status and vector DB info
```

#### Test Chatbot Q&A
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I get from Colombo to Kandy?"}'
# Expected: AI-generated answer based on transit guide
```

### Travel Planning API Testing

#### Test Legacy Route Planning (Fast)
```bash
curl -X POST "http://localhost:8000/api/v1/shortest-path" \
  -H "Content-Type: application/json" \
  -d '{"start": "Colombo", "end": "Kandy", "mode": "driving"}'
# Expected: Direct Google Maps route with 29 steps (~1 second)
```

#### Test Multi-Agent Travel Planning (Advanced)
```bash
curl -X POST "http://localhost:8000/api/v1/travel/plan-route" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "source": "Colombo", "destination": "Kandy", "mode": "driving"}'
# Expected: AI-optimized route with recommendation scores (~1-2 seconds)
```

#### Test Transit Mode Planning
```bash
curl -X POST "http://localhost:8000/api/v1/travel/plan-route" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "source": "Times Square, New York", "destination": "Brooklyn Bridge, New York", "mode": "transit"}'
# Expected: Complex multi-agent processing (~15 seconds)
```

#### Test Uber Mode Planning
```bash
curl -X POST "http://localhost:8000/api/v1/travel/plan-route" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "source": "Colombo", "destination": "Kandy", "mode": "uber"}'
# Expected: Uber route optimization
```

#### Test Active Disruptions
```bash
curl http://localhost:8000/api/v1/travel/active-disruptions
# Expected: Current traffic/transit disruptions (if any)
```

### Error Handling Testing

#### Test Invalid Input Handling
```bash
curl -X POST "http://localhost:8000/api/v1/shortest-path" \
  -H "Content-Type: application/json" \
  -d '{"start": "", "end": "Kandy", "mode": "driving"}'
# Expected: Error response for empty start location
```

#### Test Invalid City Weather
```bash
curl http://localhost:8000/api/v1/weather/current/InvalidCityName
# Expected: Error response for invalid city
```

### Performance Testing

#### Endpoint Response Times (Expected)
- **Health checks**: < 100ms
- **Weather APIs**: 200-500ms
- **Legacy route planning**: < 1 second
- **Multi-agent planning (driving)**: 1-2 seconds
- **Multi-agent planning (transit)**: 5-15 seconds
- **Chatbot Q&A**: 200-800ms

### Access Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

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
- **🌤️ Weather Integration**: OpenWeather API with travel advice generation
- **🛣️ Google Maps Integration**: Real-time routing and directions (legacy API limitations)
- **📊 Disruption Monitoring**: Active traffic/transit disruption tracking
- **👤 User Preferences**: Learning and recommendation system

### ⚠️ **Optional Features (Configurable)**
- **🔍 Web Search**: Disabled (requires SERPER_API_KEY)
- **📈 LLM Observability**: Disabled (requires Langfuse keys)
- **🔗 LangChain Tracing**: Disabled (requires LANGCHAIN_API_KEY)

### 🎯 **API Endpoints Status (All Tested & Working)**

#### ✅ **Core System APIs** 
- `GET /api/v1/` - Welcome endpoint
- `GET /api/v1/health` - Health check with database status
- `GET /api/v1/db-connection` - Database connection details (17 collections)

#### ✅ **Weather APIs (OpenWeather Integration)**
- `GET /api/v1/weather/` - Service status and endpoints
- `GET /api/v1/weather/current/{city}` - Real-time weather data
- `GET /api/v1/weather/forecast/{city}` - 5-day forecast (3-hour intervals)
- `GET /api/v1/weather/travel-advice/{city}` - AI travel advice
- `POST /api/v1/weather/coordinates` - Weather by lat/lng

#### ✅ **Chatbot APIs (RAG System)**
- `POST /api/v1/chatbot/ask` - AI Q&A with transit knowledge
- ChromaDB vector database operational (23 document chunks)
- Google Gemini AI integration working

#### ✅ **Travel Planning APIs**
- `POST /api/v1/shortest-path` - Direct Google Maps routing (< 1s response)
- `POST /api/v1/travel/plan-route` - Multi-agent AI planning (1-15s response)
- `GET /api/v1/travel/active-disruptions` - Disruption monitoring
- All travel modes working: driving, transit, uber, two_wheeler

#### ✅ **Error Handling & Validation**
- Input validation for empty/invalid data
- Weather API error handling for invalid cities
- Comprehensive error responses with proper HTTP status codes

### 🚀 **Production Ready**
Backend is fully operational with core functionality including weather integration. The system now provides comprehensive travel planning with real-time weather data and travel advice. Optional features (web search, LLM observability) can be enabled by adding the respective API keys to the `.env` file.

### 🌤️ **Weather APIs**

#### Weather Service Status
- **GET** `/api/v1/weather/`
  - Returns weather service status and available endpoints
  - Response:
    ```json
    {
      "message": "Weather API is running",
      "service": "OpenWeather API",
      "available": true,
      "endpoints": {
        "current": "/current/{city}",
        "forecast": "/forecast/{city}",
        "travel_advice": "/travel-advice/{city}",
        "coordinates": "/coordinates"
      }
    }
    ```

#### Current Weather
- **GET** `/api/v1/weather/current/{city}`
  - Get current weather for a specific city
  - Example: `/api/v1/weather/current/Colombo`
  - Response:
    ```json
    {
      "status": "success",
      "city": "Colombo",
      "country": "LK",
      "weather": {
        "main": "Clouds",
        "description": "overcast clouds",
        "temperature": 26.27,
        "feels_like": 26.27,
        "humidity": 83,
        "pressure": 1009,
        "visibility": 10.0,
        "wind_speed": 4.3,
        "wind_direction": 219,
        "cloudiness": 100
      },
      "coordinates": {"lat": 6.9319, "lng": 79.8478},
      "timestamp": "2025-09-10T03:40:14.799667"
    }
    ```

#### Weather Forecast
- **GET** `/api/v1/weather/forecast/{city}?days=5`
  - Get weather forecast for a city (1-5 days)
  - Query parameter: `days` (optional, default: 5, max: 5)
  - Returns 40 forecast entries (3-hour intervals for 5 days)
  - Response: Array of forecast objects with temperature, weather, humidity, wind, etc.

#### Travel Weather Advice
- **GET** `/api/v1/weather/travel-advice/{city}`
  - Get AI-generated travel advice based on current weather
  - Returns personalized travel recommendations

#### Weather by Coordinates
- **POST** `/api/v1/weather/coordinates`
  - Get weather data by latitude and longitude
  - Request body:
    ```json
    {
      "lat": 6.9271,
      "lng": 79.8612
    }
    ```

### 🌤️ **Weather Integration Highlights**
- **Real-time weather data** for any city using OpenWeather API
- **Travel advice generation** based on current weather conditions
- **5-day weather forecasts** for trip planning (3-hour intervals)
- **Coordinate-based weather lookup** for precise location data
- **Automated weather consideration** in multi-agent travel planning
- **Weather health checks** and API status monitoring