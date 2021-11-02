from pydantic import BaseModel, EmailStr


class Data(BaseModel):
    """ Data """

    recipient: EmailStr
    subject: str
    template: str
    data: dict
    token: str
    user_id: int


class Message(BaseModel):
    """ Message """

    msg: str
