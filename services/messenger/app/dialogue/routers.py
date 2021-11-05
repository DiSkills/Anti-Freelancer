from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dialogue import views
from app.dialogue.schemas import GetDialogue
from app.permission import is_active
from db import get_db

dialogues_router = APIRouter()


@dialogues_router.get(
    '/',
    name='Get all dialogue for user',
    description='Get all dialogue for user',
    response_description='Dialogues',
    status_code=status.HTTP_200_OK,
    response_model=list[GetDialogue],
    tags=['dialogue'],
)
async def get_all_dialogues_for_user(user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.get_all_dialogues_for_user(db, user_id)


@dialogues_router.get(
    '/{pk}',
    name='Get dialogue',
    description='Get dialogue',
    response_description='Dialogue',
    status_code=status.HTTP_200_OK,
    response_model=GetDialogue,
    tags=['dialogue'],
)
async def get_dialogue(pk: int, user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.get_dialogue(db, user_id, pk)
