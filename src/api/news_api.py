from fastapi import APIRouter, Depends, status, Query
from fastapi.templating import Jinja2Templates

from core.db import get_db
from database.models.base import User
from sqlalchemy.ext.asyncio import AsyncSession
from services import user_service, news_service
from schemas import news_schemas

router = APIRouter(prefix="/news", tags=["работа с новостями"])
templates = Jinja2Templates(directory="templates")

@router.get("/{slug}/get", response_model=news_schemas.NewsInfoResponse)
async def get_news(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    return await news_service.get_news(db,slug)

@router.get("/last/get", response_model=news_schemas.ListOfNewsInfoResponse)
async def get_public_contests(
    last: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await news_service.get_list_of_last_news(db,last)

@router.post("/set")
async def set_news(
    data:news_schemas.CreateNewsInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    return await news_service.create_news(db,user,data)

