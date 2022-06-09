from pydantic import BaseModel


class Message(BaseModel):
    """ Message """

    msg: str
