from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import requests
from app.crud import feedback_crud
from app.feedback.schemas import CreateFeedback, UpdateFeedback
from app.models import Feedback
from app.service import paginate
from config import SERVER_OTHER_BACKEND, API


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


@paginate(
    feedback_crud.all,
    feedback_crud.exist_page,
    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/',
)
async def get_all_feedbacks(*, db: AsyncSession, page: int, page_size: int, queryset: list[Feedback]):
    """
        Get all feedbacks
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param queryset: Feedbacks
        :type queryset: list
        :return: Feedbacks
    """
    ids = [feedback.user_id for feedback in queryset]
    users = await requests.get_users(ids)
    return (
        {
            **feedback.__dict__,
            'user': users[f'{feedback.user_id}'],
        } for feedback in queryset
    )


async def get_feedback(db: AsyncSession, pk: int) -> dict:
    """
        Get feedback
        :param db: DB
        :type db: AsyncSession
        :param pk: Feedback ID
        :type pk: int
        :return: Feedback
        :rtype: dict
        :raise HTTPException 400: Feedback not found
    """

    if not await feedback_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Feedback not found')
    feedback = await feedback_crud.get(db, id=pk)
    user = await requests.get_user(feedback.user_id)
    return {**feedback.__dict__, 'user': user}


async def update_feedback(db: AsyncSession, pk: int, schema: UpdateFeedback) -> dict:
    """
        Update feedback
        :param db: DB
        :type db: AsyncSession
        :param pk: Feedback ID
        :type pk: int
        :param schema: New feedback data
        :type schema: UpdateFeedback
        :return: Feedback
        :rtype: dict
        :raise HTTPException 400: Feedback not found
    """

    if not await feedback_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Feedback not found')
    feedback = await feedback_crud.update(db, {'id': pk}, **schema.dict())
    user = await requests.get_user(feedback.user_id)
    return {**feedback.__dict__, 'user': user}


async def delete_feedback(db: AsyncSession, pk: int) -> dict[str, str]:
    """
        Delete feedback
        :param db: DB
        :type db: AsyncSession
        :param pk: Feedback ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Feedback not found
    """

    if not await feedback_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Feedback not found')
    await feedback_crud.remove(db, id=pk)
    return {'msg': 'Feedback has been deleted'}
