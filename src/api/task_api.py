from fastapi import APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from services.task_service import get_task_info, edit_task, create_task, delete_task
from services.user_service import get_current_user
from services.solution_service import task_solution
from database.core.db import get_db
from database.models.base import User
from schemas.task_schemas import TaskInfoResponse, CreateTaskInput, EditTaskInput
from schemas.solution_schemas import SubmitAnswerInput, SubmitAnswerResponse

router = APIRouter(prefix="/contest", tags=["работа с тасками"])
templates = Jinja2Templates(directory="templates")


@router.get("/{contest_slug}/task/{task_slug}/get", response_model=TaskInfoResponse)
async def get_task_handler(
    contest_slug: str,
    task_slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_task_info(db, user, contest_slug, task_slug)


@router.post("/{contest_slug}/task/set", status_code=status.HTTP_200_OK)
async def create_task_handler(
    contest_slug: str,
    data: CreateTaskInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await create_task(db, user, contest_slug, data)


@router.put("/{contest_slug}/task/{task_slug}/edit", status_code=status.HTTP_200_OK)
async def edit_task_handler(
    contest_slug: str,
    task_slug: str,
    data: EditTaskInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await edit_task(db, user, contest_slug, task_slug, data)


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


@router.post(
    "/{contest_slug}/task/{task_slug}/solution",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_solution_handler(
    contest_slug: str,
    task_slug: str,
    data: SubmitAnswerInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await task_solution(db, user, contest_slug, task_slug, data.answer)
