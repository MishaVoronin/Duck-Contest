from fastapi import APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from services import user_service, contestaccess_service, contest_service
from database.models.base import User
from schemas import contest_schemas, contest_access_schemas


router = APIRouter(prefix="/contest", tags=["работа с контестами"])
templates = Jinja2Templates(directory="templates")


@router.get("/c_{slug}/get", response_model=contest_schemas.ContestInfoResponse)
async def get_contest_info_handler(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    return await contest_service.get_contest_info(db, user, slug)


@router.post("/set", status_code=status.HTTP_200_OK)
async def create_contest_handler(
    data: contest_schemas.CreateContestInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await contest_service.create_contest(db, user, data)


@router.put("/c_{slug}/edit", status_code=status.HTTP_200_OK)
async def edit_contest_handler(
    slug: str,
    data: contest_schemas.EditContestInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await contest_service.edit_contest(db, user, slug, data)


@router.delete("/c_{slug}/delete", status_code=status.HTTP_200_OK)
async def delete_contest_handler(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await contest_service.delete_contest(db, user, slug)


@router.post("/c_{slug}/access/set", status_code=status.HTTP_200_OK)
async def set_access(
    slug: str,
    data: contest_access_schemas.CreateAccessInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await contestaccess_service.create_contest_access(db, user, slug, data)
