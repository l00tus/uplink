from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .user_validators import UserValidatorsMixin

class UserBase(BaseModel, UserValidatorsMixin):
    username: str = Field(min_length=4, max_length=32)
    full_name: str = Field(min_length=4, max_length=64)
    interests: list[str]
    bio: str | None = None
    country: str | None = None
    city: str | None = None
    
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

class UserRead(UserBase):
    id: int
    created_at: datetime
    
    # from_attributes = True allows automatic conversion from SQLAlchemy objects to Pydantic models
    class Config:
        from_attributes = True

class UserUpdate(BaseModel, UserValidatorsMixin):
    username: str | None = Field(default=None, min_length=4, max_length=32)
    full_name: str | None  = Field(default=None, min_length=4, max_length=64)
    interests: list[str] | None = None
    bio: str | None = None
    country: str | None = None
    city: str | None = None

class UserDelete(BaseModel):
    message: str