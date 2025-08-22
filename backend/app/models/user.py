from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class User(Document):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None
    favorite_routes: List[str] = []
    preferences: Optional[dict] = {}

    class Settings:
        name = "users"


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    favorite_routes: Optional[List[str]] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    favorite_routes: List[str] = []
    preferences: Optional[dict] = {}