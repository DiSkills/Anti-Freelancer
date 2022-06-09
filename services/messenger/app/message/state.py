from fastapi import WebSocket

from app.message.service import websocket_error
from config import SUCCESS


class WebSocketState:
    """ Websocket state """

    def __init__(self):
        self._websockets: dict[int, list[WebSocket]] = {}

    @property
    def get_websockets(self) -> dict[int, list[WebSocket]]:
        """
            Get active current websockets
            :return: State
            :rtype: dict
        """
        return self._websockets

    def add(self, user_id: int, websocket: WebSocket) -> None:
        """
            Add to state
            :param user_id: User ID
            :type user_id: int
            :param websocket: Websocket
            :type websocket: WebSocket
            :return: None
        """
        if user_id not in self._websockets.keys():
            self._websockets[user_id] = []
        self._websockets[user_id].append(websocket)

    async def leave(self, user_id: int, websocket: WebSocket) -> None:
        """
            Leave from state
            :param user_id: User ID
            :type user_id: int
            :param websocket: Websocket
            :type websocket: WebSocket
            :return: None
        """
        if user_id not in self._websockets.keys():
            await websocket_error(websocket, {'msg': 'User is not in state'})
            return

        for index in range(len(self._websockets[user_id])):
            if self._websockets[user_id][index] == websocket:
                await self._websockets[user_id][index].close()
                del self._websockets[user_id][index]
                if len(self._websockets[user_id]) == 0:
                    del self._websockets[user_id]
                break

    async def send(self, sender_id: int, recipient_id: int, success_msg: str, response_type: str, data: dict) -> None:
        """
            Send
            :param sender_id: Sender ID
            :type sender_id: int
            :param recipient_id: Recipient ID
            :type recipient_id: int
            :param success_msg: Success message
            :type success_msg: str
            :param response_type: Response type
            :type response_type: str
            :param data: Data
            :type data: dict
            :return: None
        """
        for socket in self._websockets[sender_id]:
            await socket.send_json(
                {
                    'type': SUCCESS,
                    'data': {'msg': success_msg},
                }
            )

        sockets = self._websockets[sender_id][:]
        if recipient_id in self._websockets.keys():
            sockets += self._websockets[recipient_id]

        for socket in sockets:
            await socket.send_json(
                {
                    'type': response_type,
                    'data': data,
                }
            )
