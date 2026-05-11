from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from services.task_service import get_task_info, edit_task, create_task, delete_task
from schemas.task import TaskInfoResponse, CreateTaskInput, EditTaskInput
from database.core.db import get_db
from services.user_service import get_current_user
from database.models.base import User

router = APIRouter(prefix="/task", tags=["работа с тасками"])
templates = Jinja2Templates(directory="templates")


@router.get("/{contest_slug}/task/{task_slug}", response_model=TaskInfoResponse)
async def get_task_handler(
    contest_slug: str,
    task_slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_task_info(db, user, contest_slug, task_slug)


@router.post("/{contest_slug}/task/set")
async def create_task_handler(
    contest_slug: str,
    data: CreateTaskInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await create_task(db, user, contest_slug, data)
    return RedirectResponse(
        url=f"/contest/{contest_slug}/task/{data.slug}/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.put("/{contest_slug}/task/{task_slug}/edit")
async def edit_task_handler(
    contest_slug: str,
    task_slug: str,
    data: EditTaskInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await edit_task(db, user, contest_slug, task_slug, data)
    return RedirectResponse(
        url=f"/contest/{contest_slug}/task/{task_slug}/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.delete(
    "/{contest_slug}/task/{task_slug}/delete", status_code=status.HTTP_200_OK
)
async def delete_task_handler(
    contest_slug: str,
    task_slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await delete_task(db, user, contest_slug, task_slug)
    return None
