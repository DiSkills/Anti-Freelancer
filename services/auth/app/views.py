from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud, verification_crud
from app.schemas import Register, VerificationCreate
from app.send_email import send_register_email
from app.service import get_password_hash
from config import SERVER_BACKEND, API


async def register(db: AsyncSession, schema: Register) -> dict[str, str]:
    """
        Register
        :param db: DB
        :type db: AsyncSession
        :param schema: Register data
        :type schema: Register
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Username or email exist
    """

    if await user_crud.exist(db, username=schema.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')

    if await user_crud.exist(db, email=schema.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')

    del schema.confirm_password
    user = await user_crud.create(db, **{**schema.dict(), 'password': get_password_hash(schema.password)})

    verification = await verification_crud.create(db, **VerificationCreate(user_id=user.id, link=str(uuid4())).dict())

    send_register_email(user.email, user.username, f'{SERVER_BACKEND}{API}/verify?link={verification.link}')

    return {'msg': 'Send email for activate your account'}


async def verify(db: AsyncSession, link: str) -> dict[str, str]:
    """
        Verification account
        :param db: DB
        :type db: AsyncSession
        :param link: Link
        :type link: str
        :return: Message
        :rtype: dict
    """

    if not await verification_crud.exist(db, link=link):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification not exist')

    verification = await verification_crud.get(db, link=link)
    await user_crud.update(db, {'id': verification.user_id}, is_active=True)
    await verification_crud.remove(db, id=verification.id)
    return {'msg': 'Your account has been activated'}
