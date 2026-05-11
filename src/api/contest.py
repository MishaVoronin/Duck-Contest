from fastapi import APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from services.contest_service import (
    get_contest_info,
    create_contest,
    edit_contest,
    delete_contest,
)
from services.user_service import get_current_user
from schemas.contest import ContestInfoResponse, CreateContestInput, EditContestInput
from database.core.db import get_db
from database.models.base import User


router = APIRouter(prefix="/contest", tags=["работа с контестами"])
templates = Jinja2Templates(directory="templates")


@router.get("/{slug}/edit/", response_model=ContestInfoResponse)
async def get_contest_info_handler(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_contest_info(db, user, slug)


@router.post("/set")
async def create_contest_handler(
    data: CreateContestInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await create_contest(db, user, data)
    return RedirectResponse(
        url=f"/contest/{data.slug}/", status_code=status.HTTP_303_SEE_OTHER
    )


@router.put("/{slug}/edit/")
async def edit_contest_handler(
    slug: str,
    data: EditContestInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await edit_contest(db, user, slug, data)
    return RedirectResponse(
        url=f"/contest/{slug}/", status_code=status.HTTP_303_SEE_OTHER
    )


@router.delete("/{slug}/delete", status_code=status.HTTP_200_OK)
async def delete_contest_handler(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await delete_contest(db, user, slug)
    return None
