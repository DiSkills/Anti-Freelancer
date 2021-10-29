import datetime

from pydantic import BaseModel, validator


class CreateMessage(BaseModel):
    """ Create Message """

    msg: str
    sender_id: int
    recipient_id: int


class GetMessage(CreateMessage):
    """ Get message """

    id: int
    created_at: datetime.datetime

    @validator('created_at')
    def validate_created_at(cls, created_at: datetime.datetime):
        """ Validate created at """
        return f'{created_at}Z'.replace(' ', 'T')
