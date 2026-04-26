from database.models.base import User, UserStatusEnum
from database.core.db import get_db
import crud.user as user
import uuid
from sqlalchemy.ext.asyncio import AsyncSession


async def creatin_new_user(
    name: str, login: str, password: str, status: UserStatusEnum
) -> uuid.UUID | str:
    db: AsyncSession = get_db()

    if await user.get_user_by_login(db, login) is not None:
        return "There is a user with this login"

    new_user: User = User(name=name, login=login, password=password, status=status)

    new_user = await user.add_user_to_db(new_user)
    
    return new_user


async def get_user_by_login_and_password(login: str, password: str) -> User | str:
    db: AsyncSession = get_db()

    result: User | None = await user.get_user_by_login(db, login)
    if result is None:
        return "There is no user with this login"

    if result.password is not password:
        return "incorrect password"

    return result

    
