from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import dialogue_crud
from app.requests import get_users, get_user


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


async def get_dialogue(db: AsyncSession, user_id: int, pk: int) -> dict:
    """
        Get dialogue
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :param pk: Dialogue ID
        :type pk: int
        :return: Dialogue
        :rtype: dict
    """

    if not await dialogue_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Dialogue not found')
    dialogue = await dialogue_crud.get(db, id=pk)

    if not any(filter(lambda user: user == f'{user_id}', dialogue.users_ids.split('_'))):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You are not in this dialogue')

    user = await get_user(dialogue.get_recipient_id(user_id))
    return {**dialogue.__dict__, 'user': user}
