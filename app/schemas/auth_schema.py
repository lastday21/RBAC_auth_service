from datetime import datetime
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    full_name: str | None = None
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)
    password_confirm: str = Field(min_length=1)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    email: str | None = Field(default=None, min_length=3)
