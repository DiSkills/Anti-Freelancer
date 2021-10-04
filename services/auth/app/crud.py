from app.models import User, Verification
from app.schemas import Register, VerificationCreate
from crud import CRUD


class UserCRUD(CRUD[User, Register, Register]):
    """ User CRUD """
    pass


class VerificationCRUD(CRUD[Verification, VerificationCreate, VerificationCreate]):
    """ Verification CRUD """
    pass


user_crud = UserCRUD(User)
verification_crud = VerificationCRUD(Verification)
