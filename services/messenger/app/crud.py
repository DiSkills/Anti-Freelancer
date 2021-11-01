from app.models import Dialog, UserDialog, Message
from crud import CRUD


class DialogCRUD(CRUD[Dialog, Dialog, Dialog]):
    """ Dialog CRUD """
    pass


class UserDialogCRUD(CRUD[UserDialog, UserDialog, UserDialog]):
    """ User dialog CRUD """
    pass


class MessageCRUD(CRUD[Message, Message, Message]):
    """ Message CRUD """
    pass


dialog_crud = DialogCRUD(Dialog)
user_dialog_crud = UserDialogCRUD(UserDialog)
message_crud = MessageCRUD(Message)
