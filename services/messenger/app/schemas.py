from pydantic import BaseModel


class Message(BaseModel):
    """ Message """

    msg: str


class UserData(BaseModel):
    """ User data """

    id: int
    username: str
    avatar: str
