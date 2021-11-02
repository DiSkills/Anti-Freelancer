import json
import typing

from fastapi import WebSocket

from app.crud import dialogue_crud, message_crud
from app.message.schemas import CreateMessage, GetMessage, UserData
from app.message.service import websocket_error
from app.message.state import WebSocketState
from app.requests import sender_profile, get_user
from db import async_session


class MessengerView:

    def __init__(self):
        self._state: typing.Optional[WebSocketState] = None
        self._user_id: typing.Optional[int] = None
        self._user_data: typing.Optional[dict[str, typing.Union[str, int]]] = None

    async def connect(self, state: typing.Optional[WebSocketState], websocket: WebSocket) -> None:
        """
            Connect websocket
            :param state: Websockets state
            :type state: WebSocketState
            :param websocket: Websocket
            :type websocket: WebSocket
            :return: None
            :raise RuntimeError: State not found
        """
        if state is None:
            raise RuntimeError('State not found')
        self._state = state

        await websocket.accept()

        try:
            user_data: dict = await sender_profile(websocket.path_params.get('token'))
        except ValueError as error:
            await websocket_error(websocket, {'msg': error.args[0]})
            await websocket.close()
            return

        user_id: int = user_data.get('id')
        self._user_id = user_id
        self._user_data: typing.Optional[dict[str, typing.Union[str, int]]] = {
            'id': user_id, 'username': user_data.get('username'), 'avatar': user_data.get('avatar'),
        }
        self._state.add(self._user_id, websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """
            Disconnect websocket
            :param websocket: Websocket
            :type websocket: WebSocket
            :return: None
        """
        try:
            if self._user_id is None:
                await websocket_error(websocket, {'msg': 'User not found'})
                await websocket.close()
                return
        except AttributeError:
            return
        await self._state.leave(self._user_id, websocket)

    async def run(self, websocket: WebSocket, data: dict) -> None:
        """
            Run function on type
            :param websocket: Websocket
            :type websocket: WebSocket
            :param data: Data
            :type data: dict
            :return: None
        """
        if 'type' not in data.keys():
            await websocket_error(websocket, {'msg': 'Request type not found'})
            return

        types = {
            'SEND': (self.send_message, CreateMessage)
        }

        try:
            function, schema = types[data['type']]
            await function(websocket, schema(**{**data, 'sender_id': self._user_id}))
        except KeyError:
            await websocket_error(websocket, {'msg': 'Bad request type'})
            return
        except ValueError:
            await websocket_error(websocket, {'msg': f'Invalid {data["type"]} data'})
            return

    async def receive_json(self, websocket: WebSocket, data: str) -> None:
        """
            Receive json
            :param websocket: Websocket
            :type websocket: WebSocket
            :param data: Data
            :type data: str
            :return: None
        """
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

    async def send_message(self, websocket: WebSocket, schema: CreateMessage) -> None:
        """
            Send message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param schema: Message data
            :type schema: CreateMessage
            :return: None
        """

        if schema.sender_id not in self._state.get_websockets.keys():
            await websocket_error(websocket, {'msg': 'Sender not found'})
            return

        if schema.sender_id == schema.recipient_id:
            await websocket_error(websocket, {'msg': 'You cannot send yourself message'})
            return

        viewed = False
        if schema.recipient_id not in self._state.get_websockets.keys():
            try:
                await get_user(schema.recipient_id)
            except ValueError:
                await websocket_error(websocket, {'msg': 'Recipient not found'})
                return
        else:
            viewed = True

        async with async_session() as db:
            users_ids = f'{min(schema.sender_id, schema.recipient_id)}_{max(schema.sender_id, schema.recipient_id)}'

            if not await dialogue_crud.exist(db, users_ids=users_ids):
                dialogue = await dialogue_crud.create(db, users_ids=users_ids)
            else:
                dialogue = await dialogue_crud.get(db, users_ids=users_ids)

            msg = await message_crud.create(
                db, sender_id=schema.sender_id, viewed=viewed, msg=schema.msg, dialogue_id=dialogue.id
            )

        await self._state.send(
            sender_id=schema.sender_id,
            recipient_id=schema.recipient_id,
            success_msg='Message has been send',
            response_type='SEND',
            data=GetMessage(**{**msg.__dict__, 'viewed': False}, sender=UserData(**self._user_data)).dict()
        )
