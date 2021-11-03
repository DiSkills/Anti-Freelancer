from app.message.schemas import CreateMessage
from app.models import Dialogue, Message, Notification
from crud import CRUD


class DialogueCRUD(CRUD[Dialogue, Dialogue, Dialogue]):
    """ Dialogue CRUD """
    pass


class MessageCRUD(CRUD[Message, CreateMessage, CreateMessage]):
    """ Message CRUD """
    pass


class NotificationCRUD(CRUD[Notification, Notification, Notification]):
    """ Notification CRUD """
    pass


dialogue_crud = DialogueCRUD(Dialogue)
message_crud = MessageCRUD(Message)
notification_crud = NotificationCRUD(Notification)
