from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import dialogue_crud
from app.requests import get_users


async def get_all_dialogues_for_user(db: AsyncSession, user_id: int):
    """
        Get all dialogues for user
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :return: Dialogues
    """

    dialogues = await dialogue_crud.get_for_user(db, user_id)

    ids = [dialogue.get_recipient_id(user_id) for dialogue in dialogues]

    users = await get_users(ids)
    return (
        {
            **dialogue.__dict__,
            'user': users[f'{dialogue.get_recipient_id(user_id)}']
        } for dialogue in dialogues
    )
