import datetime

from pydantic import BaseModel, validator

from app.schemas import UserData


class CreateMessage(BaseModel):
    """ Create message """

    sender_id: int
    msg: str
    recipient_id: int


class DeleteMessage(BaseModel):
    """ Delete message """

    id: int
    sender_id: int


class UpdateMessage(DeleteMessage):
    """ Update message """

    msg: str


class GetMessage(BaseModel):
    """ Get message """

    id: int
    msg: str
    dialogue_id: int
    created_at: datetime.datetime
    viewed: bool
    sender: UserData

    @validator('created_at')
    def validate_created_at(cls, created_at: datetime.datetime):
        """ Validate created at """
        return f'{created_at}Z'.replace(' ', 'T')
