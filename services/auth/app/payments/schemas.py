from pydantic import BaseModel


class URL(BaseModel):
    """ URL """

    url: str
