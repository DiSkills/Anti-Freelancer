from app.auth.schemas import Register, VerificationCreate
from app.models import User, Verification, GitHub
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


user_crud = UserCRUD(User)
verification_crud = VerificationCRUD(Verification)
github_crud = GitHubCRUD(GitHub)
