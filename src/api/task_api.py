from fastapi import APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from services import task_service, user_service, solution_service
from core.db import get_db
from database.models.base import User
from schemas import task_schemas, solution_schemas


router = APIRouter(prefix="/contest", tags=["работа с тасками"])
templates = Jinja2Templates(directory="templates")


@router.get(
    "/c_{contest_slug}/task/t_{task_slug}/get",
    response_model=task_schemas.TaskInfoResponse,
)
async def get_task_handler(
    contest_slug: str,
    task_slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    return await task_service.get_task_info(db, user, contest_slug, task_slug)


@router.post("/c_{contest_slug}/task/set", status_code=status.HTTP_200_OK)
async def create_task_handler(
    contest_slug: str,
    data: task_schemas.CreateTaskInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await task_service.create_task(db, user, contest_slug, data)


@router.put("/c_{contest_slug}/task/t_{task_slug}/edit", status_code=status.HTTP_200_OK)
async def edit_task_handler(
    contest_slug: str,
    task_slug: str,
    data: task_schemas.EditTaskInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await task_service.edit_task(db, user, contest_slug, task_slug, data)


@router.delete(
    "/c_{contest_slug}/task/t_{task_slug}/delete", status_code=status.HTTP_200_OK
)
async def delete_task_handler(
    contest_slug: str,
    task_slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    await task_service.delete_task(db, user, contest_slug, task_slug)
    return None


@router.post(
    "/c_{contest_slug}/task/t_{task_slug}/solution",
    response_model=solution_schemas.SubmitAnswerResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_solution_handler(
    contest_slug: str,
    task_slug: str,
    data: solution_schemas.SubmitAnswerInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    return await solution_service.task_solution(
        db, user, contest_slug, task_slug, data.answer
    )
