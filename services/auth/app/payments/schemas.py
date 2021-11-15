from pydantic import BaseModel


class GetPayment(BaseModel):
    """ URL """

    url: str
    id: int
