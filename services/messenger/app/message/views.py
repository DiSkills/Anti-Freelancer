from fastapi import WebSocket, HTTPException

from app.crud import message_crud
from app.message.schemas import CreateMessage
from app.requests import get_user
from db import async_session


class WebSocketState:

    def __init__(self):
        self._users: dict[int, list[WebSocket]] = {}

    @staticmethod
    async def error(websocket: WebSocket, msg: str):
        await websocket.send_json(
            {
                'type': 'ERROR',
                'data': {'msg': msg}
            }
        )

    def add_user(self, user_id: int, websocket: WebSocket):
        if user_id not in self._users.keys():
            self._users[user_id] = []
        self._users[user_id].append(websocket)

    async def leave_user(self, user_id: int, websocket: WebSocket):
        if user_id not in self._users.keys():
            await self.error(websocket, 'User is not in state')
            return

        for i in range(len(self._users[user_id])):
            if self._users[user_id][i] == websocket:
                await self._users[user_id][i].close()
                del self._users[user_id][i]
                break

    async def message(self, websocket: WebSocket, sender_id: int, recipient_id: int, msg: str):
        if sender_id == recipient_id:
            await self.error(websocket, 'User can\'t send yourself message')
            return

        if sender_id not in self._users.keys():
            await self.error(websocket, 'Sender not found')
            return

        if recipient_id not in self._users.keys():
            try:
                await get_user(recipient_id)
            except HTTPException:
                await self.error(websocket, 'Recipient not found')
                return
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
