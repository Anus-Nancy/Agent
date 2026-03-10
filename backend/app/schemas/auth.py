from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True
