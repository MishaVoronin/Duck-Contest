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


class CreateTaskInput(BaseModel):
    slug: SlugType
    name: str
    text: str
    answer: str


class EditTaskInput(BaseModel):
    name: str
    text: str
    answer: str


class TaskInfoResponse(BaseModel):
    name: str
    text: str
    solutions: list[SolutionStatusEnum]
    is_curator: bool

class SolutionsInTaskResponse(BaseModel):
    status: SolutionStatusEnum | None
    answer: str
    submitted_at: str
