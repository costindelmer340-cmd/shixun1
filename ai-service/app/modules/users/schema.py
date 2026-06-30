from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    nickname: str
    phone: Optional[str] = None
    email: Optional[str] = None

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    bind_platform: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    avatar_url: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    bind_platform: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user: UserResponse
    token: str