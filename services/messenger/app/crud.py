from app.message.schemas import CreateMessage
from app.models import Dialogue, Message
from crud import CRUD


class DialogueCRUD(CRUD[Dialogue, Dialogue, Dialogue]):
    """ Dialogue CRUD """
    pass


class MessageCRUD(CRUD[Message, CreateMessage, CreateMessage]):
    """ Message CRUD """
    pass


dialogue_crud = DialogueCRUD(Dialogue)
message_crud = MessageCRUD(Message)
