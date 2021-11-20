from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import review_crud
from app.review.schemas import CreateReview


async def create_review(db: AsyncSession, user_id: int, schema: CreateReview) -> dict:

    if await review_crud.exist(db, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review exist')
    review = await review_crud.create(db, user_id=user_id, **schema.dict())
    return review.__dict__
