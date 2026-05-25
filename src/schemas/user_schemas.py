from pydantic import BaseModel, StringConstraints
from typing import Annotated
from database.models.base import UserStatusEnum


class RegisterUserInput(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            pattern=r"^[0-9a-zA-Z\-_]+$",
            min_length=5,
            max_length=25,
            strip_whitespace=True,
        ),
    ]
    SFP: (
        Annotated[
            str,
            StringConstraints(
                pattern=r"^[0-9a-zA-Z\-_]+$",
                min_length=5,
                max_length=25,
                strip_whitespace=True,
            ),
        ]
        | None
    )
    login: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=50,
            strip_whitespace=True,
        ),
    ]
    password: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=50,
            strip_whitespace=True,
        ),
    ]


class LoginInput(BaseModel):
    login: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=50,
            strip_whitespace=True,
        ),
    ]
    password: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=50,
            strip_whitespace=True,
        ),
    ]


class UserInfo(BaseModel):
    name: str
    SFP: str | None
    status: UserStatusEnum


class UserInfoResponse(BaseModel):
    user_info: UserInfo
    is_moderator: bool
    is_me: bool
