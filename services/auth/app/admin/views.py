import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schemas import RegisterAdmin
from app.crud import user_crud, github_crud
from app.security import get_password_hash
from app.service import paginate
from config import SERVER_BACKEND, API


@paginate(user_crud, f'{SERVER_BACKEND}{API}/admin/users')
async def get_all_users(*, db: AsyncSession, page: int, page_size: int, queryset: list):
    """
        Get all users
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


async def get_user(db: AsyncSession, user_id: int) -> dict[str, typing.Any]:
    """
        Get user
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :return: User
        :rtype: dict
        :raise HTTPException 400: User not found
    """

    if not await user_crud.exist(db, id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')
    user = await user_crud.get(db, id=user_id)
    return {**user.__dict__, 'github': user.github.__dict__ if user.github else None}


async def create_user(db: AsyncSession, schema: RegisterAdmin) -> dict[str, str]:
    """
        Create user
        :param db: DB
        :type db: AsyncSession
        :param schema: User data
        :type schema: RegisterAdmin
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Username or email exist
    """

    if await user_crud.exist(db, username=schema.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')

    if await user_crud.exist(db, email=schema.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')

    del schema.confirm_password
    await user_crud.create(db, **{**schema.dict(), 'password': get_password_hash(schema.password)})
    return {'msg': 'User has been created'}


async def unbind_github(db: AsyncSession, pk: int) -> dict[str, str]:
    """
        Unbind GitHub
        :param db: DB
        :type db: AsyncSession
        :param pk: GitHub ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: GitHub account not found
    """

    if not await github_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='GitHub account not found')

    await github_crud.remove(db, id=pk)
    return {'msg': 'GitHub account has been deleted'}
