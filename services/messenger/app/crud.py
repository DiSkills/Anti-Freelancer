from app.models import Dialog, Message
from crud import CRUD


class DialogCRUD(CRUD[Dialog, Dialog, Dialog]):
    """ Dialog CRUD """
    pass


class MessageCRUD(CRUD[Message, Message, Message]):
    """ Message CRUD """
    pass


dialog_crud = DialogCRUD(Dialog)
message_crud = MessageCRUD(Message)
