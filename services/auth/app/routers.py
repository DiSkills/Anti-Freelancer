from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import views
from app.schemas import Register
from db import get_db

auth_router = APIRouter()


@auth_router.post(
    '/register',
)
async def register(schema: Register, db: AsyncSession = Depends(get_db)):
    return await views.register(db, schema)
