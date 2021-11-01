import json
import typing

from fastapi import WebSocket

from app.crud import dialog_crud, message_crud
from app.message.schemas import CreateMessage, GetMessage
from app.message.service import websocket_error
from app.message.state import WebSocketState
from app.requests import sender_profile, get_user
from db import async_session


class MessengerView:

    def __init__(self):
        self._state: typing.Optional[WebSocketState] = None
        self._user_id: typing.Optional[int] = None
        self._user_data: typing.Optional[dict[str, typing.Union[str, int]]] = None

    async def connect(self, state: typing.Optional[WebSocketState], websocket: WebSocket):
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

    async def send_message(self, websocket: WebSocket, schema: CreateMessage):

        if schema.sender_id not in self._state._websockets.keys():
            await websocket_error(websocket, {'msg': 'Sender not found'})
            return

        if schema.recipient_id not in self._state._websockets.keys():
            try:
                await get_user(schema.recipient_id)
            except ValueError:
                await websocket_error(websocket, {'msg': 'Recipient not found'})
                return

        async with async_session() as db:
            if schema.dialog_id is None:
                sender_recipient_dialog_exist = await dialog_crud.exist(db, users_ids=f'{schema.sender_id}_{schema.recipient_id}')
                recipient_sender_dialog_exist = await dialog_crud.exist(db, users_ids=f'{schema.recipient_id}_{schema.sender_id}')
                if (
                    (not sender_recipient_dialog_exist)
                        and
                    (not recipient_sender_dialog_exist)
                ):
                    dialog = await dialog_crud.create(db, users_ids=f'{schema.sender_id}_{schema.recipient_id}')
                    dialog_id = dialog.id
                elif sender_recipient_dialog_exist:
                    dialog = await dialog_crud.get(db, users_ids=f'{schema.sender_id}_{schema.recipient_id}')
                    dialog_id = dialog.id
                elif recipient_sender_dialog_exist:
                    dialog = await dialog_crud.get(db, users_ids=f'{schema.recipient_id}_{schema.sender_id}')
                    dialog_id = dialog.id

            elif (
                (not await dialog_crud.exist(db, users_ids=f'{schema.sender_id}_{schema.recipient_id}', id=schema.dialog_id))
                    and
                (not await dialog_crud.exist(db, users_ids=f'{schema.recipient_id}_{schema.sender_id}', id=schema.dialog_id))
            ):
                await websocket_error(websocket, {'msg': 'Dialog not found'})
                return
            else:
                dialog_id = schema.dialog_id
            dialog = await dialog_crud.get(db, id=dialog_id)

            viewed = False
            if schema.recipient_id in self._state._websockets.keys():
                viewed = True
            msg = await message_crud.create(
                db, sender_id=schema.sender_id, viewed=viewed, msg=schema.msg, dialog_id=dialog.id
            )
        await self._state.send(
            sender_id=schema.sender_id,
            recipient_id=schema.recipient_id,
            success_msg='Message has been send',
            response_type='SEND',
            data=GetMessage(**{**msg.__dict__, 'viewed': False}).dict()
        )
