import json
import typing

from fastapi import APIRouter, WebSocket, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.endpoints import WebSocketEndpoint

from app.message import views
from app.message.schemas import CreateMessage, UpdateMessage, DeleteMessage, MessagePaginate
from app.message.views import WebSocketState
from app.permission import is_active
from app.requests import sender_profile
from db import get_db

message_router = APIRouter()


@message_router.get(
    '/messages',
    name='Get all messages',
    description='Get all messages',
    response_description='Messages',
    status_code=status.HTTP_200_OK,
    response_model=MessagePaginate,
    tags=['messages'],
)
async def get_messages(
    recipient_id: int,
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
    sender_id: int = Depends(is_active),
):
    return await views.get_messages(
        db=db,
        sender_id=sender_id,
        recipient_id=recipient_id,
        page=page,
        page_size=page_size
    )


@message_router.websocket_route('/ws/{token}')
class Messenger(WebSocketEndpoint):
    """ Messenger route """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state: typing.Optional[WebSocketState] = None
        self._user_id: typing.Optional[int] = None
        self._user_data: typing.Optional[dict[str, typing.Union[str, int]]] = None

    async def on_connect(self, websocket: WebSocket) -> None:
        state: typing.Optional[WebSocketState] = self.scope.get('websockets')
        if state is None:
            raise RuntimeError('State not found')
        self._state = state

        await websocket.accept()

        try:
            user_data: dict = await sender_profile(websocket.path_params['token'])
            user_id: int = user_data['id']
            self._user_data: dict[str, typing.Union[int, str]] = {
                'id': user_data['id'], 'username': user_data['username'], 'avatar': user_data['avatar'],
            }
        except ValueError as error:
            await self._state.error(websocket, error.args[0])
            await websocket.close()
            return

        self._user_id = user_id
        self._state.add_user(self._user_id, websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        if self._user_id is None:
            return
        await self._state.leave_user(self._user_id, websocket)

    async def send_message(self, websocket: WebSocket, data: dict) -> None:
        """
            Send message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param data: Data
            :type data: dict
            :return: None
        """
        try:
            data: dict[str, typing.Union[int, str]] = CreateMessage(
                **{**data, 'sender_id': self._user_id},
            ).dict()
        except ValueError:
            await self._state.error(websocket, 'Invalid data')
            return

        await self._state.send_message(websocket, sender_data=self._user_data, **data)

    async def update_message(self, websocket: WebSocket, data: dict) -> None:
        """
            Update message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param data: Data
            :type data: dict
            :return: None
        """

        try:
            data: dict[str, typing.Union[int, str]] = UpdateMessage(
                **{**data, 'sender_id': self._user_id},
            ).dict()
        except ValueError:
            await self._state.error(websocket, 'Invalid data')
            return

        await self._state.update_message(websocket, sender_data=self._user_data, **data)

    async def delete_message(self, websocket: WebSocket, data: dict) -> None:
        """
            Delete message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param data: Data
            :type data: dict
            :return: None
        """

        try:
            data: dict[str, int] = DeleteMessage(**{**data, 'sender_id': self._user_id}).dict()
        except ValueError:
            await self._state.error(websocket, 'Invalid data')
            return

        await self._state.delete_message(websocket, **data)

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        if self._user_id is None:
            raise RuntimeError('User not found')

        data = json.loads(data)
        if 'type' not in data.keys():
            await self._state.error(websocket, 'Request type not found')
            return

        types = {
            'SEND': self.send_message,
            'UPDATE': self.update_message,
            'DELETE': self.delete_message,
        }

        try:
            await types[data['type']](websocket, data)
        except KeyError:
            await self._state.error(websocket, 'Bad request type')
            return
