import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from config import API
from db import engine, Base
from main import app


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def async_loop(function):
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(function)
    finally:
        pass


class BaseTest:

    def setUp(self) -> None:
        self.session = AsyncSession(engine)
        self.client = TestClient(app)
        self.url = f'/{API}'
        async_loop(create_all())
        self.user2 = {'username': 'test2', 'id': 2, 'avatar': 'http://localhost:8000/media/test2/lol.png'}
        self.user = {'username': 'test', 'id': 1, 'avatar': 'http://localhost:8000/media/test/lol.png'}

    def tearDown(self) -> None:
        async_loop(self.session.close())
        async_loop(engine.dispose())
        async_loop(drop_all())