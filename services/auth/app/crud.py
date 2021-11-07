import uuid

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import Register, VerificationCreate
from app.models import User, Verification, GitHub, Skill, UserSkill
from crud import CRUD


class UserCRUD(CRUD[User, Register, Register]):
    """ User CRUD """

    async def create(self, db: AsyncSession, **kwargs) -> User:
        """
            Create user
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: New user
        """
        return await super().create(db, referral_link=f'{uuid.uuid4()}', **kwargs)

    @staticmethod
    async def get_by_ids(db: AsyncSession, ids: list[int]) -> list[User]:
        """
            Get by ids
            :param db: DB
            :type db: AsyncSession
            :param ids: IDs
            :type ids: list
            :return: Users
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(User).filter(
                User.id.in_(ids)
            )
        )
        return query.scalars().all()

    @staticmethod
    async def freelancers(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        """
            Freelancers
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Freelancers
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(User).filter_by(
                freelancer=True
            ).order_by(User.level.desc(), User.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()

    @staticmethod
    async def freelancers_exist(db: AsyncSession, skip: int = 0, limit: int = 100) -> bool:
        """
            Freelancers exist?
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Freelancers exist?
            :rtype: bool
        """
        query = await db.execute(
            sqlalchemy.exists(
                sqlalchemy.select(User.id).filter_by(freelancer=True).order_by(
                    User.level.desc(), User.id.desc()
                ).offset(skip).limit(limit)
            ).select()
        )
        return query.scalar()

    @staticmethod
    async def search(db: AsyncSession, search: str, skip: int = 0, limit: int = 100) -> list[User]:
        """
            Search freelancers
            :param db: DB
            :type db: AsyncSession
            :param search: Search
            :type search: str
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Freelancers
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(User).filter(
                sqlalchemy.and_(
                    User.username.ilike(f'%{search}%'),
                    User.freelancer == True,
                ),
            ).order_by(User.level.desc(), User.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()

    @staticmethod
    async def search_exist(db: AsyncSession, search: str, skip: int = 0, limit: int = 100) -> bool:
        """
            Search freelancers exist?
            :param db: DB
            :type db: AsyncSession
            :param search: Search
            :type search: str
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Search freelancers exist?
            :rtype: bool
        """
        query = await db.execute(
            sqlalchemy.exists(
                sqlalchemy.select(User).filter(
                    sqlalchemy.and_(
                        User.username.ilike(f'%{search}%'),
                        User.freelancer == True,
                    ),
                ).order_by(User.level.desc(), User.id.desc()).offset(skip).limit(limit)
            ).select()
        )
        return query.scalar()


class VerificationCRUD(CRUD[Verification, VerificationCreate, VerificationCreate]):
    """ Verification CRUD """
    pass


class GitHubCRUD(CRUD[GitHub, GitHub, GitHub]):
    """ GitHub CRUD """
    pass


class SkillCRUD(CRUD[Skill, Skill, Skill]):
    """ Skill CRUD """

    async def create_from_file(self, db: AsyncSession, data_list: list[list[str]], **kwargs) -> list[Skill]:
        """
            Create from file
            :param db: DB
            :type db: AsyncSession
            :param data_list: Skills data
            :type data_list: list
            :param kwargs: Kwargs
            :return: New skills
            :rtype: list
        """
        instances = []
        for data in data_list:
            if (await self.exist(db, image=data[0])) or (await self.exist(db, name=data[1])):
                continue
            new_instance = await self.create(db, image=data[0], name=data[1], **kwargs)
            instances.append(new_instance.__dict__)
        return instances


class UserSkillCRUD(CRUD[UserSkill, UserSkill, UserSkill]):
    """ User Skill CRUD """
    pass


user_crud = UserCRUD(User)
verification_crud = VerificationCRUD(Verification)
github_crud = GitHubCRUD(GitHub)
skill_crud = SkillCRUD(Skill)
user_skill_crud = UserSkillCRUD(UserSkill)
