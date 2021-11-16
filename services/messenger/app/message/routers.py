import typing

from fastapi import APIRouter, WebSocket, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.endpoints import WebSocketEndpoint

from app.message import views
from app.message.schemas import MessagesPaginate
from app.message.state import WebSocketState
from app.permission import is_active
from app.schemas import Message
from db import get_db

message_router = APIRouter()


@message_router.get(
    '/dialogue',
    name='Messages for dialogue',
    description='Messages for dialogue',
    response_description='Messages',
    status_code=status.HTTP_200_OK,
    response_model=MessagesPaginate,
    tags=['messages'],
)
async def get_messages_for_dialogue(
    dialogue_id: int,
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    user_id: int = Depends(is_active),
    db: AsyncSession = Depends(get_db),
):
    return await views.get_messages_for_dialogue(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        dialogue_id=dialogue_id,
    )


@message_router.put(
    '/view',
    name='View messages',
    description='View messages',
    response_description='Message',
    response_model=Message,
    status_code=status.HTTP_200_OK,
    tags=['messages'],
)
async def view_messages(
    ids: list[int],
    dialogue_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(is_active)
):
    return await views.view_messages(db=db, user_id=user_id, ids=ids, dialogue_id=dialogue_id)


@message_router.websocket_route('/ws/{token}')
class MessengerRouter(WebSocketEndpoint, views.MessengerView):

    async def on_connect(self, websocket: WebSocket) -> None:
        state: typing.Optional[WebSocketState] = self.scope.get('websockets')
        await self.connect(state, websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.disconnect(websocket)

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        await self.receive_json(websocket, data)
