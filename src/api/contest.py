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
from services.task_service import get_task_info, edit_task, create_task, delete_task
from services.user_service import get_current_user
from services.solution_service import task_solution
from database.core.db import get_db
from database.models.base import User
from schemas.contest import ContestInfoResponse, CreateContestInput, EditContestInput
from schemas.task import TaskInfoResponse, CreateTaskInput, EditTaskInput
from schemas.solution import SubmitAnswerInput

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


router.post(
    "/{contest_slug}/task/{task_slug}/solution",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)


async def submit_solution_handler(
    contest_slug: str,
    task_slug: str,
    data: SubmitAnswerInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    status_enum = await task_solution(db, user, contest_slug, task_slug, data.answer)
    return {
        "status": status_enum.value if hasattr(status_enum, "value") else status_enum
    }
