import json
import typing

from fastapi import APIRouter, WebSocket
from starlette.endpoints import WebSocketEndpoint

from app.message.schemas import CreateMessage
from app.message.views import WebSocketState
from app.requests import sender_profile

message_router = APIRouter()


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

        await self._state.message(websocket, sender_data=self._user_data, **data)

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        if self._user_id is None:
            raise RuntimeError('User not found')

        data = json.loads(data)
        if 'type' not in data.keys():
            await self._state.error(websocket, 'Request type not found')
            return

        if 'SEND' == data['type']:
            await self.send_message(websocket, data)
        else:
            await self._state.error(websocket, 'Bad request type')
            return
