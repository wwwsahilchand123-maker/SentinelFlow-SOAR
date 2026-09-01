from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.user import RoleEnum

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.SOC_ANALYST

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: RoleEnum
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
