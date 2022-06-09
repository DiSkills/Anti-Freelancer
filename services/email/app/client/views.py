import typing
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client_crud


async def get_all_clients(db: AsyncSession):
    """
        Get all clients
        :param db: DB
        :type db: AsyncSession
        :return: Clients
    """

    return (client.__dict__ for client in await client_crud.all(db, limit=1000))


async def create_client(db: AsyncSession, client_name: str) -> dict[str, typing.Union[str, int]]:
    """
        Create client
        :param db: DB
        :type db: AsyncSession
        :param client_name: Client name
        :type client_name: str
        :return: New client
        :rtype: dict
        :raise HTTPException 400: Client exist
    """

    if await client_crud.exist(db, client_name=client_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client exist')

    client = await client_crud.create(db, secret=f'{uuid.uuid4()}', client_name=client_name)
    return client.__dict__


async def create_or_get_client(db: AsyncSession, client_name: str) -> dict[str, typing.Union[str, int]]:
    """
        Create or get client
        :param db: DB
        :type db: AsyncSession
        :param client_name: Client name
        :type client_name: str
        :return: Client
        :rtype: dict
    """

    if await client_crud.exist(db, client_name=client_name):
        client = await client_crud.get(db, client_name=client_name)
    else:
        client = await client_crud.create(db, secret=f'{uuid.uuid4()}', client_name=client_name)
    return client.__dict__


async def get_client(db: AsyncSession, pk: int) -> dict[str, typing.Union[str, int]]:
    """
        Get client
        :param db: DB
        :type db: AsyncSession
        :param pk: Client ID
        :type pk: int
        :return: Client
        :rtype: dict
        :raise HTTPException 400: Client not found
    """
    if not await client_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    client = await client_crud.get(db, id=pk)
    return client.__dict__


async def update_client(db: AsyncSession, pk: int) -> dict[str, typing.Union[str, int]]:
    """
        Update client secret
        :param db: DB
        :type db: AsyncSession
        :param pk: Client ID
        :type pk: int
        :return: Client
        :rtype: dict
        :raise HTTPException 400: Client not found
    """
    if not await client_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    client = await client_crud.update(db, {'id': pk}, secret=f'{uuid.uuid4()}')
    return client.__dict__


async def delete_client(db: AsyncSession, pk: int) -> dict[str, str]:
    """
        Delete client
        :param db: DB
        :type db: AsyncSession
        :param pk: Client ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Client not found
    """
    if not await client_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    await client_crud.remove(db, id=pk)
    return {'msg': 'Client has been deleted'}
