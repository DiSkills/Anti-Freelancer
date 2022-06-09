import uuid

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import requests
from app.crud import payment_crud, user_crud
from app.models import User
from config import PUBLIC_QIWI_KEY


async def pay(db: AsyncSession, user: User, amount: int) -> dict[str, str]:
    """
        Pay
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :param amount: Amount
        :type amount: int
        :return: URL
        :rtype: dict
    """

    if await payment_crud.exist(db, user_id=user.id, is_completed=False):
        await payment_crud.remove(db, user_id=user.id, is_completed=False)
    payment = await payment_crud.create(
        db, uuid=str(uuid.uuid4()), amount=amount, comment=f'Buy level for user {user.username}', user_id=user.id
    )

    _url = f'https://oplata.qiwi.com/create?' \
           f'publicKey={PUBLIC_QIWI_KEY}&billId={payment.uuid}&amount={payment.amount}&comment={payment.comment}'

    payment_url = await requests.pay_request(_url)
    return {'url': f'{payment_url}', **payment.__dict__}


async def check(db: AsyncSession,  pk: int) -> dict[str, str]:
    """
        Check payment and level up
        :param db: DB
        :type db: AsyncSession
        :param pk: Payment ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Payment not found
        :raise HTTPException 400: The purchase has already been credited
        :raise HTTPException 400: Payment not paid
    """

    if not await payment_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Payment not found')
    payment = await payment_crud.get(db, id=pk)

    if payment.is_completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The purchase has already been credited')

    response = await requests.check_request(f'https://api.qiwi.com/partner/bill/v1/bills/{payment.uuid}')

    if response.get('status').get('value') != 'PAID':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Payment not paid')

    user = await user_crud.get(db, id=payment.user_id)
    await user_crud.update(db, {'id': user.id}, level=user.level + payment.amount)
    await payment_crud.update(db, {'id': payment.id}, is_completed=True)
    return {'msg': 'Level has been up'}
