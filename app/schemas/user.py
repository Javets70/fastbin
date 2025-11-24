import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, Field


def validate_password_strength(v: str) -> str:
    """Validate password meets all strength requirements."""

    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one digit")

    if not re.search(r"[@$!%*?&]", v):
        raise ValueError(
            "Password must contain at least one special character (@$!%*?&)"
        )

    return v


class UserCreate(BaseModel):
    email: EmailStr
    password: Field(
        ..., min_length=8, description="Password must be atleast 8 characters long"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLogin(BaseModel):
    email: EmailStr
    password: Field(
        ..., min_length=8, description="Password must be atleast 8 characters long"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str
