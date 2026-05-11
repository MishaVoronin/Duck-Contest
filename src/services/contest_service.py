from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import (
    add_contest,
    get_contest_by_slug,
    delete_contest_from_db,
    update_contest,
)
from crud.contest_access import get_access_by_user_and_contest
from crud.task import get_tasks_by_contest_id
from database.models.base import User, UserStatusEnum, Contest, ContestAccess
from fastapi import HTTPException, status
from schemas.contest import CreateContestInput, EditContestInput


async def get_contest_info(  # contest/(slug:str)/
    db: AsyncSession, user: User, contest_slug: str
) -> dict:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    contest_dict: dict = {
        "name": contest.name,
        "tasks": await get_tasks_by_contest_id(db, contest.id),
        "is_curator": False,
    }

    if contest.curator_id == user.id:
        contest_dict["is_curator"] = True
        return contest_dict

    access: ContestAccess | None = await get_access_by_user_and_contest(
        db, user.id, contest.id
    )

    if not contest.is_active or access is None and not contest.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )
    else:
        return contest_dict


async def create_contest(
    db: AsyncSession, user: User, data: CreateContestInput
) -> dict:

    if user.status is not UserStatusEnum.CURATOR:
        raise HTTPException(status_code=403, detail="The user is not a curator")

    if await get_contest_by_slug(db, data.slug) is not None:
        raise HTTPException(status_code=409, detail="There is a contest with this slug")

    contest = Contest(
        name=data.name,
        curator_id=user.id,
        slug=data.slug,
        text=data.text,
        is_active=False,
        is_public=data.is_public,
    )
    contest = await add_contest(db, contest)

    return await get_contest_info(db, user, data.slug)


async def edit_contest(
    db: AsyncSession, user: User, contest_slug: str, data: EditContestInput
) -> dict:
    contest = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")

    if contest.curator_id != user.id:
        raise HTTPException(
            status_code=403, detail="You do not have access to this contest"
        )

    contest = await update_contest(
        db,
        contest,
        contest_name=data.contest_name,
        is_active=data.is_active,
        is_public=data.is_public,
    )

    return await get_contest_info(db, user, contest_slug)


async def delete_contest(db: AsyncSession, user: User, contest_slug: str) -> None:
    contest = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    if contest.curator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contest",
        )

    await delete_contest_from_db(db, contest)
