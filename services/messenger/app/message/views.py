import typing

from fastapi import WebSocket

from app.message.service import websocket_error
from app.message.state import WebSocketState
from app.requests import sender_profile


class MessengerView:

    def __init__(self):
        self._state: typing.Optional[WebSocketState] = None
        self._user_id: typing.Optional[int] = None

    async def connect(self, state: typing.Optional[WebSocketState], websocket: WebSocket):
        if state is None:
            raise RuntimeError('State not found')
        self._state = state

        await websocket.accept()

        try:
            user_data: dict = await sender_profile(websocket.path_params.get('token'))
            user_id: int = user_data.get('id')
            self._user_id = user_id
        except ValueError as error:
            await websocket_error(websocket, {'msg': error.args[0]})
            await websocket.close()
            return

        self._state.add(self._user_id, websocket)

    async def disconnect(self, websocket: WebSocket):
        if self._user_id is None:
            await websocket_error(websocket, {'msg': 'User not found'})
            return
        await self._state.leave(self._user_id, websocket)
