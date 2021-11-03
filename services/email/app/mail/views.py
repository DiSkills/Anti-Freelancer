import os

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client_crud
from app.mail.schemas import SendData
from config import TEST
from tasks import send_email


async def send(db: AsyncSession, schema: SendData) -> dict[str, str]:
    """
        Send
        :param db: DB
        :type db: AsyncSession
        :param schema: Send data
        :type schema: SendData
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Client not found
        :raise HTTPException 400: Bad client secret
        :raise HTTPException 400: Template not found
    """

    if not await client_crud.exist(db, client_name=schema.client_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')

    client = await client_crud.get(db, client_name=schema.client_name)

    if client.secret != schema.secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad client secret')

    if not os.path.exists(f'templates/{schema.template}'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Template not found')

    if not int(TEST):
        send_email.delay(schema.recipient, schema.subject, f'templates/{schema.template}', **schema.data)
    return {'msg': 'Email has been send'}
