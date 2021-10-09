from pydantic import BaseModel


class CreateSkill(BaseModel):

    name: str
    image: str


class UpdateSkill(CreateSkill):
    pass


class GetSkill(CreateSkill):

    id: int
