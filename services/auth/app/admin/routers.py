from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import views
from app.admin.schemas import UsersPaginate
from app.views import is_superuser
from db import get_db

admin_router = APIRouter()


@admin_router.get(
    '/users',
    name='Users admin',
    description='Users admin',
    response_description='Users',
    status_code=status.HTTP_200_OK,
    response_model=UsersPaginate,
    tags=['admin'],
    dependencies=[Depends(is_superuser)],
)
async def admin_users_all(
        page: int = Query(default=1, gt=0),
        page_size: int = Query(default=1, gt=0),
        db: AsyncSession = Depends(get_db),
):
    return await views.admin_users_all(db=db, page=page, page_size=page_size)
