import datetime
import typing

from pydantic import BaseModel, Field, validator

from app.schemas import Paginate


class CreateJob(BaseModel):

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

        if (
                order_date.date() < datetime.datetime.utcnow().date()
        ) or (
                order_date.time() < datetime.datetime.utcnow().time()
        ):
            raise ValueError('Date can\'t be past')
        return order_date


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
