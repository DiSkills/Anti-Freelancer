import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dialog, Message
from crud import CRUD


class DialogCRUD(CRUD[Dialog, Dialog, Dialog]):
    """ Dialog CRUD """

    async def exist_for_users(self, db: AsyncSession, sender_id: int, recipient_id: int, **kwargs):
        sender_recipient = f'{sender_id}_{recipient_id}'
        recipient_sender = f'{recipient_id}_{sender_id}'

        query = await db.execute(sqlalchemy.exists(sqlalchemy.select(Dialog.id).filter_by(**kwargs).filter(
            sqlalchemy.or_(
                Dialog.users_ids == sender_recipient,
                Dialog.users_ids == recipient_sender,
            )
        )).select())
        return query.scalar()

    async def get_for_users(self, db: AsyncSession, sender_id: int, recipient_id: int):
        sender_recipient = f'{sender_id}_{recipient_id}'
        recipient_sender = f'{recipient_id}_{sender_id}'
        query = await db.execute(sqlalchemy.select(Dialog).filter(
            sqlalchemy.or_(
                Dialog.users_ids == sender_recipient,
                Dialog.users_ids == recipient_sender,
            )
        ))
        return query.scalars().first()


class MessageCRUD(CRUD[Message, Message, Message]):
    """ Message CRUD """
    pass


dialog_crud = DialogCRUD(Dialog)
message_crud = MessageCRUD(Message)
