from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.security import get_password_hash


async def createsuperuser(db: AsyncSession, username: str, password: str, email: str) -> None:
    """
        Create superuser
        :param db: DB
        :type db: AsyncSession
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        :param email: Email
        :type email: str
        :return: None
    """

    if len(await user_crud.all(db, limit=2)):
        return

    await user_crud.create(
        db, username=username, email=email, password=get_password_hash(password), is_superuser=True, is_active=True,
    )
