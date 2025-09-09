from fastapi import APIRouter
from app.chatbot.chatbot import router as chatbot_router

# Create the main router for chatbot endpoints
router = APIRouter()

# Include the chatbot router with appropriate prefix and tags
router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
