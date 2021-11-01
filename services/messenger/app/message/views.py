import json
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
            await websocket.close()
            return
        await self._state.leave(self._user_id, websocket)

    async def run(self, websocket: WebSocket, data: dict):
        if 'type' not in data.keys():
            await websocket_error(websocket, {'msg': 'Request type not found'})
            return

        types = {
        }

        try:
            await types[data['type']](websocket, data)
        except KeyError:
            await websocket_error(websocket, {'msg': 'Bad request type'})
            return

    async def receive_json(self, websocket: WebSocket, data: str):
        if self._user_id is None:
            await websocket_error(websocket, {'msg': 'User not found'})
            await websocket.close()
            return

        try:
            data = json.loads(data)
        except Exception as _ex:
            print(_ex)
            await websocket_error(websocket, {'msg': 'Invalid data'})
            return

        await self.run(websocket, data)
