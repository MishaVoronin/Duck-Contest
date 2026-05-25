from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from crud import contest_crud, contest_access_crud, user_crud
from schemas import contest_access_schemas
from database.models.base import User, Contest, ContestAccess


async def create_contest_access(
    db: AsyncSession,
    user: User,
    slug: str,
    data: contest_access_schemas.CreateAccessInput,
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest: Contest | None = await contest_crud.get_contest_by_slug(db, slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    if user.id is not contest.curator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contest",
        )

    added_user: ContestAccess | None = await user_crud.get_user_by_name(db, data.name)
    if added_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    access = await contest_access_crud.get_access_by_user_and_contest(
        db, added_user.id, contest.id
    )
    if access is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already has access to this contest",
        )

    await contest_access_crud.add_access(
        ContestAccess(user_id=added_user.id, contest_id=contest.id)
    )


async def delite_contest_access(db: AsyncSession, user: User, slug: str, data: dict):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest: Contest | None = await contest_crud.get_contest_by_slug(db, slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    if user.id is not contest.curator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contest",
        )

    added_user: User | None = await user_crud.get_user_by_name(db, data.name)
    if added_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    access: (
        ContestAccess | None
    ) = await contest_access_crud.get_access_by_user_and_contest(
        db, added_user.id, contest.id
    )
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already hasn't access to this contest",
        )

    await contest_access_crud.delete_contest_access_from_db(db, access)
