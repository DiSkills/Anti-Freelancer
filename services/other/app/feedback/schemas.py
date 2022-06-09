import datetime

from pydantic import BaseModel, validator

from app.schemas import Paginate


class CreateFeedback(BaseModel):
    """ Create feedback """

    text: str


class UpdateFeedback(CreateFeedback):
    """ Update feedback """

    status: bool


class GetFeedback(UpdateFeedback):
    """ Get feedback """

    id: int
    created_at: datetime.datetime
    user_id: int

    @validator('created_at')
    def validate_created_at(cls, created_at: datetime.datetime):
        """ Validate created at """
        return f'{created_at}Z'.replace(' ', 'T')


class PaginateFeedbacks(Paginate):
    """ Paginate feedback """

    results: list[GetFeedback]
