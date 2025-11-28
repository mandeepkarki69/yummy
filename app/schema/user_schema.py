from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    
class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    
class AdminRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role : str
    access_token: str
    token_type: str
    
    class Config:
        orm_mode = True

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_by: int

    class Config:
        orm_mode = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_name: str
    email: EmailStr
    user_role: str
    
    class Config:
        orm_mode = True
    
     
class TokenData(BaseModel):
    id: Optional[str] = None
