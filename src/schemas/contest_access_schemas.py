from pydantic import BaseModel


class CreateAccessInput(BaseModel):
    user: str
