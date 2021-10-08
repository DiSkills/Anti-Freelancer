from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.service import paginate
from config import SERVER_BACKEND, API


@paginate(user_crud, f'{SERVER_BACKEND}{API}/admin/users')
async def admin_users_all(*, db: AsyncSession, page: int, page_size: int, queryset: list):
    """
        Users all for admin
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: str
        :param queryset: Queryset
        :type queryset: list
        :return: Users
    """
    return (user.__dict__ for user in queryset)
