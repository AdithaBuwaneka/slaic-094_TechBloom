from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, test_db_connection
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    print("Connected to MongoDB")
    
    # Test connection
    if await test_db_connection():
        print("MongoDB connection test successful")
    else:
        print("MongoDB connection test failed")
    
    yield
    
    # Shutdown
    await close_mongo_connection()
    print("Disconnected from MongoDB")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Smart Transit Companion Backend API
    
    A comprehensive FastAPI backend providing intelligent transit assistance with AI-powered features.
    
    ### 🚀 Key Features
    - **99 Fully Functional Endpoints** (96 HTTP + 3 WebSocket)
    - **AI-Powered Transit Intelligence** with multiple specialized agents
    - **Real-time Data Processing** and WebSocket connections
    - **Multi-modal Journey Planning** with optimization
    - **Accessibility-First Design** with inclusive features
    - **Multi-language Support** with real-time translation
    - **MongoDB Integration** with async operations
    
    ### 📊 API Categories
    - **🤖 AI Agents**: Route optimization, fare calculation, accessibility assistance
    - **📊 Data Management**: Real-time transit data and analytics
    - **🛤️ Route Planning**: Multi-modal route calculation and optimization
    - **👤 Personalization**: User-specific customization and preferences
    - **💰 Fare Optimization**: Smart fare calculation and cost optimization
    - **♿ Accessibility**: Inclusive design and accessibility features
    - **🌐 Language Support**: Multi-language support and translation
    - **⚠️ Disruption Management**: Real-time service disruption handling
    - **🏘️ Local Knowledge**: Location-specific insights and recommendations
    - **🔌 WebSocket**: Real-time communication channels
    
    ### 🧪 Testing
    - **100% Endpoint Coverage** with comprehensive test suite
    - **Automated Testing** with fast execution modes
    - **Real-time Monitoring** and health checks
    
    ### 🔗 Documentation
    - **Interactive API Explorer**: Use the interface below to test endpoints
    - **Complete Endpoint Documentation**: All 99 endpoints documented
    - **Example Requests**: Ready-to-use API calls for testing
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Smart Transit Companion Team",
        "url": "https://example.com/contact/",
        "email": "support@smarttransit.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.smarttransit.com",
            "description": "Production server"
        }
    ],
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)