import json
import typing

from fastapi import APIRouter, WebSocket
from starlette.endpoints import WebSocketEndpoint

from app import requests
from app.message.schemas import CreateMessage
from app.message.views import WebSocketState

message_router = APIRouter()


@message_router.websocket_route('/ws/{user_id}')
class Messenger(WebSocketEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state: typing.Optional[WebSocketState] = None
        self._user_id: typing.Optional[int] = None

    async def on_connect(self, websocket: WebSocket) -> None:
        state: typing.Optional[WebSocketState] = self.scope.get('websockets')
        if state is None:
            raise RuntimeError('State not found')
        self._state = state

        user_id: int = int(websocket.path_params['user_id'])
        self._user_id = user_id
        await requests.get_user(user_id)

        await websocket.accept()
        self._state.add_user(self._user_id, websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        if self._user_id is None:
            raise RuntimeError('User not found')
        await self._state.leave_user(self._user_id, websocket)

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        if self._user_id is None:
            raise RuntimeError('User not found')

        data: dict[str, typing.Union[int, str]] = json.loads(data)

        await self._state.message(websocket, **CreateMessage(**data).dict())
