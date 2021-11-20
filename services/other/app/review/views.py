from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import review_crud
from app.models import Review
from app.review.schemas import CreateReview
from app.service import paginate
from config import SERVER_OTHER_BACKEND, API


async def create_review(db: AsyncSession, user_id: int, schema: CreateReview) -> dict:
    """
        Create review
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :param schema: New review data
        :type schema: CreateReview
        :return: New review
        :rtype: dict
        :raise HTTPException 400: Review exist
    """

    if await review_crud.exist(db, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review exist')
    review = await review_crud.create(db, user_id=user_id, **schema.dict())
    return review.__dict__


@paginate(review_crud.sorting, review_crud.exist_sorting, f'{SERVER_OTHER_BACKEND}{API}/reviews/', 'sort')
async def get_all_reviews(*, db: AsyncSession, page: int, page_size: int, sort: str, queryset: list[Review]):
    return (review.__dict__ for review in queryset)
