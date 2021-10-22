import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CreateCategory, UpdateCategory
from app.jobs.schemas import CreateJob, UpdateJob
from app.models import SuperCategory, SubCategory, Job
from crud import CRUD


class SuperCategoryCRUD(CRUD[SuperCategory, CreateCategory, UpdateCategory]):
    """ Super category CRUD """
    pass


class SubCategoryCRUD(CRUD[SubCategory, CreateCategory, UpdateCategory]):
    """ Sub category CRUD """
    pass


class JobCRUD(CRUD[Job, CreateJob, UpdateJob]):
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
    async def all_for_category_without_completed(
            db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100
    ) -> list[Job]:
        """
            All for category without completed
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
            sqlalchemy.select(Job).filter_by(
                category_id=category_id, completed=False, executor_id=None
            ).order_by(Job.id.desc()).offset(skip).limit(limit)
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
                sqlalchemy.and_(
                    sqlalchemy.or_(
                        Job.title.ilike(f'%{search}%'),
                        Job.description.ilike(f'%{search}%'),
                    ),
                    Job.completed == False,
                    Job.executor_id == None
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
                    sqlalchemy.and_(
                        sqlalchemy.or_(
                            Job.title.ilike(f'%{search}%'),
                            Job.description.ilike(f'%{search}%'),
                        ),
                        Job.completed == False,
                        Job.executor_id == None
                    )
                ).order_by(Job.id.desc()).offset(skip).limit(limit)
            ).select()
        )
        return query.scalar()

    async def get_all_active_jobs(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Job]:
        """
            Get all active jobs
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Jobs
            :rtype: list
        """
        return await super().filter(db, skip, limit, completed=False, executor_id=None)

    async def exist_page_active_jobs(self, db: AsyncSession, skip: int = 0, limit: int = 100, **kwargs) -> bool:
        """
            Page with active jobs exist?
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Page with active jobs exist?
            :rtype: bool
        """
        return await super().exist_page(db, skip, limit, completed=False, executor_id=None, **kwargs)

    async def filter_jobs_for_freelancer(self, db: AsyncSession, pk: int, skip: int = 0, limit: int = 100) -> list[Job]:
        """
            Filter jobs for freelancer
            :param db: DB
            :type db: AsyncSession
            :param pk: Freelancer ID
            :type pk: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Jobs
            :rtype: list
        """
        return await super().filter(db, skip, limit, executor_id=pk)

    async def exist_page_for_freelancer_jobs(self, db: AsyncSession, pk: int, skip: int = 0, limit: int = 100) -> bool:
        """
            Exist page for freelancer jobs
            :param db: DB
            :type db: AsyncSession
            :param pk: Freelancer ID
            :type pk: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Exist page for freelancer jobs?
            :rtype: bool
        """
        return await super().exist_page(db, skip, limit, executor_id=pk)

    async def filter_jobs_for_customer(self, db: AsyncSession, pk: int, skip: int = 0, limit: int = 100) -> list[Job]:
        """
            Filter jobs for customer
            :param db: DB
            :type db: AsyncSession
            :param pk: Customer ID
            :type pk: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Jobs
            :rtype: list
        """
        return await super().filter(db, skip, limit, customer_id=pk)

    async def exist_page_for_customer_jobs(self, db: AsyncSession, pk: int, skip: int = 0, limit: int = 100) -> bool:
        """
            Exist page for customer jobs
            :param db: DB
            :type db: AsyncSession
            :param pk: Customer ID
            :type pk: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Exist page for customer jobs?
            :rtype: bool
        """
        return await super().exist_page(db, skip, limit, customer_id=pk)


super_category_crud = SuperCategoryCRUD(SuperCategory)
sub_category_crud = SubCategoryCRUD(SubCategory)
job_crud = JobCRUD(Job)
