from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import Register, VerificationCreate
from app.models import User, Verification, GitHub, Skill, UserSkill
from crud import CRUD


class UserCRUD(CRUD[User, Register, Register]):
    """ User CRUD """
    pass


class VerificationCRUD(CRUD[Verification, VerificationCreate, VerificationCreate]):
    """ Verification CRUD """
    pass


class GitHubCRUD(CRUD[GitHub, GitHub, GitHub]):
    """ GitHub CRUD """
    pass


class SkillCRUD(CRUD[Skill, Skill, Skill]):
    """ Skill CRUD """

    async def create_from_file(self, db: AsyncSession, data_list: list[list], **kwargs) -> list[Skill]:
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
