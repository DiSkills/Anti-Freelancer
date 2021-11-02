from pydantic import BaseModel


class Data(BaseModel):
    """ Data """

    recipient: str
    subject: str
    template: str
    data: dict
    token: str
    user_id: int


class Message(BaseModel):
    """ Message """

    msg: str
