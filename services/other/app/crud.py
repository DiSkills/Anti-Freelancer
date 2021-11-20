import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.feedback.schemas import CreateFeedback
from app.models import Feedback, Review
from app.review.schemas import CreateReview
from crud import CRUD


class FeedbackCRUD(CRUD[Feedback, CreateFeedback, CreateFeedback]):
    """ Feedback CRUD """

    @staticmethod
    async def sorting(db: AsyncSession, skip: int = 0, limit: int = 100, desc: bool = False) -> list[Feedback]:
        """
            Sort
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :param desc: Sort is DESC?
            :type desc: bool
            :return: Feedbacks
            :rtype: list
        """
        sort = Feedback.status.asc()
        if desc:
            sort = Feedback.status.desc()

        query = await db.execute(
            sqlalchemy.select(Feedback).order_by(sort, Feedback.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()

    @staticmethod
    async def exist_sorting(db: AsyncSession, skip: int = 0, limit: int = 100, desc: bool = False, **kwargs) -> bool:
        """
            Exist sort page?
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :param desc: Sort is DESC?
            :type desc: bool
            :return: Exist sort page?
            :rtype: bool
        """
        sort = Feedback.status.asc()
        if desc:
            sort = Feedback.status.desc()

        query = await db.execute(
            sqlalchemy.exists(
                sqlalchemy.select(Feedback.id).filter_by(**kwargs).order_by(
                    sort, Feedback.id.desc()
                ).offset(skip).limit(limit)
            ).select()
        )
        return query.scalar()


class ReviewCRUD(CRUD[Review, CreateReview, CreateReview]):
    """ Review CRUD """
    pass


feedback_crud = FeedbackCRUD(Feedback)
review_crud = ReviewCRUD(Review)
