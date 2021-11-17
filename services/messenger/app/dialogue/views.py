from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import dialogue_crud
from app.service import dialogue_exist


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

    return (
        {
            **dialogue.__dict__,
        } for dialogue in dialogues
    )


@dialogue_exist('pk', 'user_id')
async def get_dialogue(*, db: AsyncSession, user_id: int, pk: int) -> dict:
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

    dialogue = await dialogue_crud.get(db, id=pk)

    return {**dialogue.__dict__}
