from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import review_crud
from app.models import Review
from app.review.schemas import CreateReview, UpdateReview
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
    """
        Get all reviews
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param sort: Sort
        :type sort: str
        :param queryset: Reviews
        :type queryset: list
        :return: Reviews
    """
    return (review.__dict__ for review in queryset)


async def get_review(db: AsyncSession, pk: int) -> dict:
    """
        Get review
        :param db: DB
        :type db: AsyncSession
        :param pk: Review ID
        :type pk: int
        :return: Review
        :rtype: dict
        :raise HTTPException 400: Review not found
    """

    if not await review_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review not found')
    review = await review_crud.get(db, id=pk)
    return review.__dict__


async def update_review(db: AsyncSession, pk: int, schema: UpdateReview, user_id: int, is_admin: bool = False) -> dict:
    """
        Update review
        :param db: DB
        :type db: AsyncSession
        :param pk: Review ID
        :type pk: int
        :param schema: Update review data
        :type schema: UpdateReview
        :param user_id: User ID
        :type user_id: int
        :param is_admin: User is admin?
        :type is_admin: bool
        :return: Review
        :rtype: dict
        :raise HTTPException 400: Review not found
        :raise HTTPException 400: User not owner this review
    """

    if not await review_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review not found')
    review = await review_crud.get(db, id=pk)

    if (review.user_id != user_id) and (not is_admin):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not owner this review')
    review = await review_crud.update(db, {'id': pk}, **schema.dict())
    return review.__dict__
