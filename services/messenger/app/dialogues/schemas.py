from pydantic import BaseModel

from app.schemas import UserData


class GetDialogue(BaseModel):
    """ Get dialogue """

    id: int
    user: UserData
