from pydantic import BaseModel

from app.message.schemas import GetMessage


class GetNotification(BaseModel):
    """ Get notification """

    id: int
    type: str
    data: GetMessage
