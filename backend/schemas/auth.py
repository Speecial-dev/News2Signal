from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

_pw_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")  # min 8, küçük, büyük, rakam

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if _pw_regex.match(v) is None:
            raise ValueError("Password must be at least 8 characters long, include one uppercase letter, one lowercase letter, and one number.")
        return v

class RegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
