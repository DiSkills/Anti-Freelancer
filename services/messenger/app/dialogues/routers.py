from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dialogues import views
from app.dialogues.schemas import GetDialogue
from app.permission import is_active
from db import get_db

dialogues_router = APIRouter()


@dialogues_router.get(
    '/',
    name='Get all dialogues for user',
    description='Get all dialogues for user',
    response_description='Dialogues',
    status_code=status.HTTP_200_OK,
    response_model=list[GetDialogue],
    tags=['messages'],
)
async def get_all_dialogues_for_user(user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.get_all_dialogues_for_user(db, user_id)
