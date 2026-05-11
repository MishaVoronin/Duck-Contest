from pydantic import BaseModel, StringConstraints
from typing import Annotated

SlugType = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-zA-Z\-_]+$", min_length=1, max_length=255, strip_whitespace=True
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
    is_curator: bool
