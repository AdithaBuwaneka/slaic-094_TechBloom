from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, test_db_connection
from app.api import journey_planner
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Check for API Key on startup
if not os.getenv('GOOGLE_MAPS_API_KEY') or "YOUR_API_KEY_HERE" in os.getenv('GOOGLE_MAPS_API_KEY'):
    raise ValueError("GOOGLE_MAPS_API_KEY is not set or is invalid. Please check your .env file.")

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


app.include_router(journey_planner.router, prefix="/api/v1", tags=["Journey Planning"])