import datetime

from pydantic import BaseModel, validator


class SenderData(BaseModel):
    """ Sender data """

    id: int
    username: str
    avatar: str


class CreateMessage(BaseModel):
    """ Create message """

    msg: str
    sender_id: int
    recipient_id: int


class DeleteMessage(BaseModel):
    """ Delete message """

    msg_id: int
    sender_id: int


class UpdateMessage(DeleteMessage):
    """ Update message """

    msg: str


class GetMessage(CreateMessage):
    """ Get message """

    id: int
    created_at: datetime.datetime
    viewed: bool

    sender: SenderData

    @validator('created_at')
    def validate_created_at(cls, created_at: datetime.datetime):
        """ Validate created at """
        return f'{created_at}Z'.replace(' ', 'T')
