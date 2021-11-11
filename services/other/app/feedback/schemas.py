from pydantic import BaseModel


class CreateFeedback(BaseModel):
    """ Create feedback """

    text: str
