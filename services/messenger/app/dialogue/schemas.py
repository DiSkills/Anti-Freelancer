from pydantic import BaseModel


class GetDialogue(BaseModel):
    """ Get dialogue """

    id: int
    users_ids: str
