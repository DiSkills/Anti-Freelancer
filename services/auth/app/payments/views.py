import uuid

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import payment_crud
from app.models import User
from config import PUBLIC_QIWI_KEY


async def pay_request(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        response = await session.get(url, allow_redirects=True)
        response.raise_for_status()
    return f'{response.url}'


async def pay(db: AsyncSession, user: User, amount: int) -> dict[str, str]:
    if await payment_crud.exist(db, user_id=user.id, is_completed=False):
        await payment_crud.remove(db, user_id=user.id, is_completed=False)
    payment = await payment_crud.create(
        db, uuid=str(uuid.uuid4()), amount=amount, comment=f'Buy level for user {user.username}', user_id=user.id
    )

    _url = f'https://oplata.qiwi.com/create?' \
           f'publicKey={PUBLIC_QIWI_KEY}&billId={payment.uuid}&amount={payment.amount}&comment={payment.comment}'

    url = await pay_request(_url)
    return {'url': f'{url}'}
