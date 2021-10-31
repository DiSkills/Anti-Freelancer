import typing

from pydantic import BaseModel


class Message(BaseModel):
    """ Message """

    msg: str


class Paginate(BaseModel):
    """ Paginate """

    next: typing.Optional[str]
    previous: typing.Optional[str]
    page: int
    results: list
