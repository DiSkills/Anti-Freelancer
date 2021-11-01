from app.models import Dialog, UserDialog, Message
from crud import CRUD


class DialogCRUD(CRUD[Dialog, Dialog, Dialog]):
    pass


class UserDialogCRUD(CRUD[UserDialog, UserDialog, UserDialog]):
    pass


class MessageCRUD(CRUD[Message, Message, Message]):
    pass


dialog_crud = DialogCRUD(Dialog)
user_dialog_crud = UserDialogCRUD(UserDialog)
message_crud = MessageCRUD(Message)
