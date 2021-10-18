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

    @staticmethod
    async def search(db: AsyncSession, search: str, skip: int = 0, limit: int = 100) -> list[Job]:
        """
            Search
            :param db: DB
            :type db: AsyncSession
            :param search: Search
            :type search: str
            :param skip: Skip
            :type skip: str
            :param limit: Limit
            :type limit: str
            :return: Jobs
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(Job).filter(
                sqlalchemy.or_(
                    Job.title.ilike(f'%{search}%'),
                    Job.description.ilike(f'%{search}%'),
                )
            ).order_by(Job.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()

    @staticmethod
    async def search_exist(db: AsyncSession, search: str, skip: int = 0, limit: int = 100) -> bool:
        """
            Search exist
            :param db: DB
            :type db: AsyncSession
            :param search: Search
            :type search: str
            :param skip: Skip
            :type skip: str
            :param limit: Limit
            :type limit: str
            :return: Jobs exist?
            :rtype: bool
        """
        query = await db.execute(
            sqlalchemy.exists(
                sqlalchemy.select(Job.id).filter(
                    sqlalchemy.or_(
                        Job.title.ilike(f'%{search}%'),
                        Job.description.ilike(f'%{search}%'),
                    )
                ).order_by(Job.id.desc()).offset(skip).limit(limit)
            ).select()
        )
        return query.scalar()


super_category_crud = SuperCategoryCRUD(SuperCategory)
sub_category_crud = SubCategoryCRUD(SubCategory)
job_crud = JobCRUD(Job)
