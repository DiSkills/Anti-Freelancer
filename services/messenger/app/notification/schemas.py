from pydantic import BaseModel

from app.message.schemas import GetMessage


class GetNotification(BaseModel):

    id: int
    type: str
    data: GetMessage
