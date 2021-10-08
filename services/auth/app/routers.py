from fastapi import APIRouter, Depends, status

from app import views
from app.models import User
from app.schemas import PermissionResponse

permission_router = APIRouter()


@permission_router.post(
    '/is-authenticated',
    name='Authenticated user',
    description='Authenticated user',
    response_description='User ID',
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    tags=['permission'],
)
async def is_authenticated(user_id: int = Depends(views.is_authenticated)):
    return {'user_id': user_id}


@permission_router.post(
    '/is-active',
    name='Is activated user',
    description='Is activated user',
    response_description='User ID',
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    tags=['permission'],
)
async def is_active(user: User = Depends(views.is_active)):
    return {'user_id': user.id}


@permission_router.post(
    '/is-superuser',
    name='Is superuser user',
    description='Is superuser user',
    response_description='User ID',
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    tags=['permission'],
)
async def is_superuser(user: User = Depends(views.is_superuser)):
    return {'user_id': user.id}
