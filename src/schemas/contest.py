from pydantic import BaseModel, StringConstraints
from typing import Annotated
from database.models.base import SolutionStatusEnum

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
    name: str
    slug: SlugType
    description:  Annotated[
    str,StringConstraints(
        min_length=1,
        strip_whitespace=True,
    )]
    is_public: bool = True


class EditContestInput(BaseModel):
    contest_name: str
    is_active: bool
    is_public: bool


class ContestInfoResponse(BaseModel):
    name: str
    tasks: list[TaskInContestResponse] | None
    description: str
    is_activ: bool
    is_curator: bool


class TaskInContestResponse(BaseModel):
    name: str
    slug: str
    status: SolutionStatusEnum | None
