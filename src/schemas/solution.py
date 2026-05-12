from pydantic import BaseModel, StringConstraints
from typing import Annotated


class SubmitAnswerInput(BaseModel):
    answer: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
    ]
