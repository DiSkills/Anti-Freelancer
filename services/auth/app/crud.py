from app.models import User
from app.schemas import Register
from crud import CRUD


class UserCRUD(CRUD[User, Register, Register]):
    """ User CRUD """
    pass


user_crud = UserCRUD(User)
