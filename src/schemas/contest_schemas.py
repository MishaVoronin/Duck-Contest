from pydantic import BaseModel, StringConstraints
from typing import Annotated

SlugType = Annotated[
    str,
    StringConstraints(
        pattern=r"^[0-9a-zA-Z\-_]+$",
        min_length=1,
        max_length=255,
        strip_whitespace=True,
    ),
]


class CreateContestInput(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=100,
            strip_whitespace=True,
        ),
    ]
    slug: SlugType
    description: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=1000,
            strip_whitespace=True,
        ),
    ]
    is_public: bool = True


class EditContestInput(BaseModel):
    contest_name: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=100,
            strip_whitespace=True,
        ),
    ]
    is_active: bool
    is_public: bool


class ContestSmallInfo(BaseModel):
    name: str
    slug: str
    description: str
    is_activ: bool


class ContestSmallInfoResponse(BaseModel):
    has_data: bool
    data: ContestSmallInfo|None

class ContestInfoResponse(BaseModel):
    name: str
    tasks: list[TaskInContestResponse] | None
    description: str
    is_activ: bool
    is_curator: bool


class TaskInContestResponse(BaseModel):
    name: str
    slug: str
    points: int
    