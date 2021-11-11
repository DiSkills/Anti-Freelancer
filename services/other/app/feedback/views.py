from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import feedback_crud
from app.feedback.schemas import CreateFeedback


async def create_feedback(db: AsyncSession, user_id: int, schema: CreateFeedback) -> dict[str, str]:
    """
        Create feedback
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :param schema: Feedback data
        :type schema: CreateFeedback
        :return: Message
        :rtype: dict
    """

    await feedback_crud.create(db, user_id=user_id, **schema.dict())
    return {'msg': 'Thanks for your feedback. Feedback has been created!'}
