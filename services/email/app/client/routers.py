from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.client import views
from app.client.schemas import GetClient
from app.permission import is_superuser
from app.schemas import Message
from db import get_db

client_router = APIRouter()


@client_router.get(
    '/',
    name='Get all clients',
    description='Get all clients',
    response_description='Clients',
    status_code=status.HTTP_200_OK,
    response_model=list[GetClient],
    tags=['clients'],
    dependencies=[Depends(is_superuser)],
)
async def get_all_clients(db: AsyncSession = Depends(get_db)):
    return await views.get_all_clients(db)


@client_router.post(
    '/',
    name='Create client',
    description='Create client',
    response_description='Client',
    status_code=status.HTTP_201_CREATED,
    response_model=GetClient,
    tags=['clients'],
    dependencies=[Depends(is_superuser)],
)
async def create_client(client_name: str, db: AsyncSession = Depends(get_db)):
    return await views.create_client(db, client_name)


@client_router.get(
    '/{pk}',
    name='Get client',
    description='Get client',
    response_description='Client',
    status_code=status.HTTP_200_OK,
    response_model=GetClient,
    tags=['clients'],
    dependencies=[Depends(is_superuser)],
)
async def get_client(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_client(db, pk)


@client_router.put(
    '/{pk}',
    name='Update client secret',
    description='Update client secret',
    response_description='Client',
    status_code=status.HTTP_200_OK,
    response_model=GetClient,
    tags=['clients'],
    dependencies=[Depends(is_superuser)],
)
async def update_client(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.update_client(db, pk)


@client_router.delete(
    '/{pk}',
    name='Delete client',
    description='Delete client',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['clients'],
    dependencies=[Depends(is_superuser)],
)
async def delete_client(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.delete_client(db, pk)
