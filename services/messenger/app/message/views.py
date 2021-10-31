import typing

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import message_crud
from app.message.schemas import CreateMessage, GetMessage, UserData
from app.message.service import get_sender, get_recipient
from app.models import Message
from app.requests import get_user
from app.service import paginate
from config import SERVER_MESSENGER_BACKEND, API
from db import async_session


@paginate(
    message_crud.get_all_for_dialog,
    message_crud.exist_all_for_dialog,
    f'{SERVER_MESSENGER_BACKEND}{API}/messages',
    'sender_id', 'recipient_id'
)
async def get_messages_for_dialog(
    *,
    db: AsyncSession,
    sender_id: int,
    recipient_id: int,
    page: int,
    page_size: int,
    queryset: list[Message],
):

    sender = await get_sender(sender_id)
    recipient = await get_recipient(recipient_id)
    response = (
        {
            **message.__dict__,
            'sender': sender if message.sender_id == sender_id else recipient,
            'recipient': recipient if message.recipient_id == recipient_id else sender,
        } for message in queryset
    )

    async with async_session() as db:
        await message_crud.update_viewed(db, sender_id, recipient_id, page_size * (page - 1), page_size)

    return response


class WebSocketState:

    def __init__(self):
        self._users: dict[int, list[WebSocket]] = {}

    @staticmethod
    async def error(websocket: WebSocket, msg: str):
        """
            Send error
            :param websocket: Websocket
            :type websocket: WebSocket
            :param msg: Message
            :type msg: str
            :return: None
        """
        await websocket.send_json(
            {
                'type': 'ERROR',
                'data': {'msg': msg}
            }
        )

    def add_user(self, user_id: int, websocket: WebSocket):
        """
            Add user
            :param user_id: User ID
            :type user_id: int
            :param websocket: Websocket
            :type websocket: WebSocket
        """
        if user_id not in self._users.keys():
            self._users[user_id] = []
        self._users[user_id].append(websocket)

    async def leave_user(self, user_id: int, websocket: WebSocket):
        """
            Leave user
            :param user_id: User ID
            :type user_id: int
            :param websocket: Websocket
            :type websocket: WebSocket
        """
        if user_id not in self._users.keys():
            await self.error(websocket, 'User is not in state')
            return

        for i in range(len(self._users[user_id])):
            if self._users[user_id][i] == websocket:
                await self._users[user_id][i].close()
                del self._users[user_id][i]
                break

    async def send_message(
        self,
        websocket: WebSocket,
        sender_id: int,
        recipient_id: int,
        msg: str,
        sender_data: dict[str, typing.Union[int, str]],
    ):
        """
            Send message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param sender_id: Sender ID
            :type sender_id: int
            :param recipient_id: Recipient ID
            :type recipient_id: int
            :param msg: Message
            :type msg: str
            :param sender_data: Sender data
            :type sender_data: dict
        """
        if sender_id == recipient_id:
            await self.error(websocket, 'User can\'t send yourself message')
            return

        if sender_id not in self._users.keys():
            await self.error(websocket, 'Sender not found')
            return

        if recipient_id not in self._users.keys():
            try:
                await get_user(recipient_id)
            except ValueError:
                await self.error(websocket, 'Recipient not found')
                return

        async with async_session() as db:
            msg = await message_crud.create(
                db, **CreateMessage(sender_id=sender_id, msg=msg, recipient_id=recipient_id).dict()
            )

        for socket in self._users[sender_id]:
            await socket.send_json(
                {
                    'type': 'SUCCESS',
                    'data': {'msg': 'Message has been send'}
                }
            )

            await socket.send_json(
                {
                    'type': 'SEND_MESSAGE',
                    'data': GetMessage(**msg.__dict__, sender=UserData(**sender_data)).dict(),
                }
            )

        if recipient_id in self._users.keys():
            for socket in self._users[recipient_id]:
                await socket.send_json(
                    {
                        'type': 'SEND_MESSAGE',
                        'data': GetMessage(**msg.__dict__, sender=UserData(**sender_data)).dict(),
                    }
                )

            async with async_session() as db:
                await message_crud.update(db, {'id': msg.id}, viewed=True)

    async def update_message(
        self,
        websocket: WebSocket,
        sender_id: int,
        msg_id: int,
        msg: str,
        sender_data: dict[str, typing.Union[int, str]],
    ):
        """
            Update message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param sender_id: Sender ID
            :type sender_id: int
            :param msg_id: Message ID
            :type msg_id: int
            :param msg: Message text
            :type msg: str
            :param sender_data: Sender data
            :type sender_data: dict
        """

        if sender_id not in self._users.keys():
            await self.error(websocket, 'Sender not found')
            return

        async with async_session() as db:

            if not await message_crud.exist(db, id=msg_id, sender_id=sender_id):
                await self.error(websocket, 'Message not found')
                return

            msg = await message_crud.update(db, {'id': msg_id}, msg=msg)

        for socket in self._users[sender_id]:
            await socket.send_json(
                {
                    'type': 'SUCCESS',
                    'data': {'msg': 'Message has been updated'}
                }
            )

            await socket.send_json(
                {
                    'type': 'UPDATE_MESSAGE',
                    'data': GetMessage(**msg.__dict__, sender=UserData(**sender_data)).dict(),
                }
            )

        if msg.recipient_id in self._users.keys():
            for socket in self._users[msg.recipient_id]:
                await socket.send_json(
                    {
                        'type': 'UPDATE_MESSAGE',
                        'data': GetMessage(**msg.__dict__, sender=UserData(**sender_data)).dict(),
                    }
                )

            async with async_session() as db:
                await message_crud.update(db, {'id': msg.id}, viewed=True)

    async def delete_message(
        self,
        websocket: WebSocket,
        sender_id: int,
        msg_id: int,
    ):
        """
            Delete message
            :param websocket: Websocket
            :type websocket: WebSocket
            :param sender_id: Sender ID
            :type sender_id: int
            :param msg_id: Message ID
            :type msg_id: int
        """

        if sender_id not in self._users.keys():
            await self.error(websocket, 'Sender not found')
            return

        async with async_session() as db:

            if not await message_crud.exist(db, id=msg_id, sender_id=sender_id):
                await self.error(websocket, 'Message not found')
                return

            msg = await message_crud.get(db, id=msg_id)
            await message_crud.remove(db, id=msg_id)

        for socket in self._users[sender_id]:
            await socket.send_json(
                {
                    'type': 'SUCCESS',
                    'data': {'msg': 'Message has been deleted'}
                }
            )

            await socket.send_json(
                {
                    'type': 'DELETE_MESSAGE',
                    'data': {'id': msg.id},
                }
            )

        if msg.recipient_id in self._users.keys():
            for socket in self._users[msg.recipient_id]:
                await socket.send_json(
                    {
                        'type': 'DELETE_MESSAGE',
                        'data': {'id': msg.id},
                    }
                )
