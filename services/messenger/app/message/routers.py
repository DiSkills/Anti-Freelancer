import json
import typing

from fastapi import APIRouter, WebSocket
from starlette.endpoints import WebSocketEndpoint

from app.message.schemas import CreateMessage
from app.message.views import WebSocketState
from app.permission import is_active

message_router = APIRouter()


@message_router.websocket_route('/ws/{token}')
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

        await websocket.accept()

        try:
            user_id: int = await is_active(websocket.path_params['token'])
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

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        if self._user_id is None:
            raise RuntimeError('User not found')

        try:
            data: dict[str, typing.Union[int, str]] = CreateMessage(
                **{**json.loads(data), 'sender_id': self._user_id},
            ).dict()
        except ValueError:
            await self._state.error(websocket, 'Invalid data')
            return

        await self._state.message(websocket, **data)
