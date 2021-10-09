from pydantic import BaseModel


class CreateSkill(BaseModel):
    """ Create skill """

    name: str
    image: str


class UpdateSkill(CreateSkill):
    """ Update skill """
    pass


class GetSkill(CreateSkill):
    """ Get skill """

    id: int
