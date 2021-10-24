from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import Register, VerificationCreate
from app.models import User, Verification, GitHub, Skill, UserSkill
from crud import CRUD


class UserCRUD(CRUD[User, Register, Register]):
    """ User CRUD """

    async def freelancers(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
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
        return await super().filter(db, skip, limit, freelancer=True)

    async def freelancers_exist(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> bool:
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
        return await super().exist_page(db, skip, limit, freelancer=True)


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
