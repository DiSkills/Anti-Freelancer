import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CreateCategory, UpdateCategory
from app.models import SuperCategory, SubCategory, Job
from crud import CRUD


class SuperCategoryCRUD(CRUD[SuperCategory, CreateCategory, UpdateCategory]):
    """ Super category CRUD """
    pass


class SubCategoryCRUD(CRUD[SubCategory, CreateCategory, UpdateCategory]):
    """ Sub category CRUD """
    pass


class JobCRUD(CRUD[Job, Job, Job]):
    """ Job CRUD """

    @staticmethod
    async def all_for_category(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100) -> list[Job]:
        """
            All for category
            :param db: DB
            :type db: AsyncSession
            :param category_id: ID category
            :type category_id: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Jobs
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(Job).filter_by(category_id=category_id).order_by(Job.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()


super_category_crud = SuperCategoryCRUD(SuperCategory)
sub_category_crud = SubCategoryCRUD(SubCategory)
job_crud = JobCRUD(Job)
