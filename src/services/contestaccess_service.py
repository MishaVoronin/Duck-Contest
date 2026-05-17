from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import get_contest_by_slug
from crud.contest_access import add_access, get_access_by_user_and_contest, delete_contest_access_from_db
from crud.user import get_user_by_name
from schemas.contest_access import CreateAccessInput
from database.models.base import User, Contest, ContestAccess
from fastapi import HTTPException, status


async def create_contest_access(
    db: AsyncSession, user: User, slug: str, data:CreateAccessInput
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest: Contest | None = await get_contest_by_slug(db, slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    if user.id is not contest.curator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contest",
        )

    added_user: ContestAccess | None = await get_user_by_name(db, data.name)
    if added_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    access = await get_access_by_user_and_contest(db, added_user.id, contest.id)
    if access is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already has access to this contest"
        )
    
    await add_access(ContestAccess(user_id=added_user.id, contest_id=contest.id))

async def delite_contest_access(db:AsyncSession,user:User,slug:str,data:dict):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest: Contest | None = await get_contest_by_slug(db, slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    if user.id is not contest.curator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contest",
        )

    added_user: User | None = await get_user_by_name(db, data.name)
    if added_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    access:ContestAccess | None  = await get_access_by_user_and_contest(db, added_user.id, contest.id)
    if access is  None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already hasn't access to this contest"
        )
    
    await delete_contest_access_from_db(db,access)