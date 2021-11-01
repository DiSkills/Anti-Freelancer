import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from config import API
from db import Base, engine
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

    @staticmethod
    def get_new_user(user_id):
        return {
            'username': f'test{user_id}', 'id': user_id, 'avatar': f'http://localhost:8000/media/test{user_id}/lol.png'
        }

    def setUp(self) -> None:
        self.session = AsyncSession(engine)
        self.client = TestClient(app)
        self.url = f'/{API}'
        async_loop(create_all())

    def tearDown(self) -> None:
        async_loop(self.session.close())
        async_loop(engine.dispose())
        async_loop(drop_all())
