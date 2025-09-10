from fastapi import APIRouter
from app.chatbot.chatbot import router as chatbot_router

# Create the main router for chatbot endpoints
router = APIRouter()

# Include the chatbot router without additional prefix (it's already at /api/v1/chatbot/)
router.include_router(chatbot_router, tags=["Chatbot"])
