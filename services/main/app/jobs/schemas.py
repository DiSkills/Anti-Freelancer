import datetime
import typing

from pydantic import BaseModel, Field, validator

from app.schemas import Paginate
from config import SERVER_MAIN_BACKEND, API


class CreateJob(BaseModel):
    """ Create job """

    title: str
    description: str
    price: int
    order_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    category_id: int

    @validator('price')
    def validate_price(cls, price):
        """ Validate price """

        if price <= 0:
            raise ValueError('The price must be at least 0')
        return price

    @validator('order_date')
    def validate_order_date(cls, order_date):
        """ Validate order date """
        if datetime.datetime.utcfromtimestamp(order_date.timestamp()).timestamp() < datetime.datetime.utcnow().timestamp():
            raise ValueError('Date can\'t be past')
        return order_date


class UpdateJob(CreateJob):
    """ Update job (owner) """
    pass


class UpdateJobAdmin(UpdateJob):
    """ Update job (admin) """
    completed: bool = False


class GetJob(BaseModel):
    """ Get job """

    id: int
    title: str
    description: str
    price: int
    order_date: datetime.datetime
    category_id: int
    customer_id: int
    executor_id: typing.Optional[int]
    completed: bool

    @validator('order_date')
    def validate_order_date(cls, order_date: datetime.datetime):
        """ Validate order date """
        return f'{order_date}Z'.replace(' ', 'T')


class JobsPaginate(Paginate):
    """ Jobs paginate """

    results: list[GetJob]


class Attachment(BaseModel):
    """ Attachment """

    id: int
    path: str

    @validator('path')
    def validate_path(cls, path: str):
        """ Validate path """
        return f'{SERVER_MAIN_BACKEND}{API}/jobs/{path}'


class AttachmentsJob(GetJob):
    """ Get job with attachments """

    attachments: list[Attachment]
