from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .role import RoleName, RoleRead


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    role: RoleName


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[RoleName] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    role: RoleRead
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


