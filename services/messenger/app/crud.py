import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dialogue, Message
from crud import CRUD


class DialogueCRUD(CRUD[Dialogue, Dialogue, Dialogue]):
    """ Dialogue CRUD """

    @staticmethod
    async def exist_by_users(db: AsyncSession, sender_id: int, recipient_id: int, **kwargs):
        sender_recipient = f'{sender_id}_{recipient_id}'
        recipient_sender = f'{recipient_id}_{sender_id}'

        query = await db.execute(sqlalchemy.exists(sqlalchemy.select(Dialogue.id).filter_by(**kwargs).filter(
            sqlalchemy.or_(
                Dialogue.users_ids == sender_recipient,
                Dialogue.users_ids == recipient_sender,
            )
        )).select())
        return query.scalar()

    @staticmethod
    async def get_by_users(db: AsyncSession, sender_id: int, recipient_id: int):
        sender_recipient = f'{sender_id}_{recipient_id}'
        recipient_sender = f'{recipient_id}_{sender_id}'
        query = await db.execute(sqlalchemy.select(Dialogue).filter(
            sqlalchemy.or_(
                Dialogue.users_ids == sender_recipient,
                Dialogue.users_ids == recipient_sender,
            )
        ))
        return query.scalars().first()


class MessageCRUD(CRUD[Message, Message, Message]):
    """ Message CRUD """
    pass


dialogue_crud = DialogueCRUD(Dialogue)
message_crud = MessageCRUD(Message)
