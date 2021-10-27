from app.models import Message
from app.message.schemas import CreateMessage
from crud import CRUD


class MessageCRUD(CRUD[Message, CreateMessage, CreateMessage]):
    """ Message CRUD """
    pass


message_crud = MessageCRUD(Message)
