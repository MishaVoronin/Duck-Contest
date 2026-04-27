from crud import user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.base import User
import scripts.auth as auth
from pydantic import BaseModel, Field, validator
from typing import Annotated

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    login: str
    #created_at: datetime
    #last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    status: Optional[UserStatusEnum] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

async def register_user(db: AsyncSession,name: str, login: str, password: str) -> User|None:
    if not await user.get_user_by_login(db,login):
        return await user.create_user(db, User(name=name,login=login, password=password))
    return None
