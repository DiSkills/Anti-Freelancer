import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client_crud


async def get_all_clients(db: AsyncSession):
    return (client.__dict__ for client in await client_crud.all(db, limit=1000))


async def create_client(db: AsyncSession, client_name: str):

    if await client_crud.exist(db, client_name=client_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client exist')

    client = await client_crud.create(db, secret=f'{uuid.uuid4()}', client_name=client_name)
    return client.__dict__


async def get_client(db: AsyncSession, pk: int):
    if not await client_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    client = await client_crud.get(db, id=pk)
    return client.__dict__


async def update_client(db: AsyncSession, pk: int):
    if not await client_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    client = await client_crud.update(db, {'id': pk}, secret=f'{uuid.uuid4()}')
    return client.__dict__


async def delete_client(db: AsyncSession, pk: int):
    if not await client_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    await client_crud.remove(db, id=pk)
    return {'msg': 'Client has been deleted'}
