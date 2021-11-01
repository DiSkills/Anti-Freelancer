import datetime
import typing

from pydantic import BaseModel, validator


class CreateMessage(BaseModel):
    sender_id: int
    msg: str
    dialogue_id: typing.Optional[int] = None
    recipient_id: int


class GetMessage(BaseModel):

    id: int
    sender_id: int
    msg: str
    dialogue_id: int
    created_at: datetime.datetime
    viewed: bool

    @validator('created_at')
    def validate_created_at(cls, created_at: datetime.datetime):
        """ Validate created at """
        return f'{created_at}Z'.replace(' ', 'T')
