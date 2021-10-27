from pydantic import BaseModel


class CreateMessage(BaseModel):
    """ Create Message """

    msg: str
    sender_id: int
    recipient_id: int
