from pydantic import BaseModel


class CreateMessage(BaseModel):

    msg: str
    sender_id: int
    recipient_id: int


class Message(BaseModel):
    """ Message """

    msg: str
