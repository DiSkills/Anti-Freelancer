from fastapi import WebSocket

from app.crud import message_crud
from app.message.schemas import CreateMessage
from app.requests import get_user
from db import async_session


class WebSocketState:

    def __init__(self):
        self._users: dict[int, list[WebSocket]] = {}

    def add_user(self, user_id: int, websocket: WebSocket):
        if user_id not in self._users.keys():
            self._users[user_id] = []
        self._users[user_id].append(websocket)

    async def leave_user(self, user_id: int, websocket: WebSocket):
        if user_id not in self._users.keys():
            raise ValueError('User is not in state')

        for i in range(len(self._users[user_id])):
            if self._users[user_id][i] == websocket:
                await self._users[user_id][i].close()
                del self._users[user_id][i]
                break

    async def message(self, sender_id: int, recipient_id: int, msg: str):
        if sender_id not in self._users.keys():
            raise ValueError('Sender not found')

        if recipient_id not in self._users.keys():
            await get_user(recipient_id)
        else:
            for socket in self._users[recipient_id]:
                await socket.send_json(
                    {
                        'type': 'MESSAGE',
                        'data': {'sender': sender_id, 'recipient': recipient_id, 'msg': msg}
                    }
                )

        async with async_session() as db:
            await message_crud.create(
                db, **CreateMessage(sender_id=sender_id, msg=msg, recipient_id=recipient_id).dict()
            )
