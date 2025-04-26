from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UsersResponse(BaseModel):
    success: bool
    message: str
    data: List[UserOut]  # List of UserOut objects
    code: int
