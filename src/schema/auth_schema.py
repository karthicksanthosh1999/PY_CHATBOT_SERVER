from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class RegisterRequest(BaseModel):
    fullName: str = Field(min_length=2, max_length=100)
    email: EmailStr
    mobile: str = Field(min_length=10)
    password: str = Field(min_length=8, max_length=120)

class UserResponse(BaseModel):
    id: int
    fullName: str
    mobile: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=120)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"