from fastapi import WebSocket


async def websocket_error(websocket: WebSocket, detail: dict):
    await websocket.send_json(
        {
            'type': 'ERROR',
            'data': {'detail': detail}
        }
    )


class WebSocketState:
    def __init__(self):
        self._websockets: dict[int, list[WebSocket]] = {}

    def add(self, user_id: int, websocket: WebSocket):
        if user_id not in self._websockets.keys():
            self._websockets[user_id] = []
        self._websockets[user_id].append(websocket)

    async def leave(self, user_id: int, websocket: WebSocket):
        if user_id not in self._websockets.keys():
            await websocket_error(websocket, {'msg': 'User is not in state'})
            return

        for index in range(len(self._websockets[user_id])):
            if self._websockets[user_id][index] == websocket:
                await self._websockets[user_id][index].close()
                del self._websockets[user_id][index]
                break

    async def send(self, sender_id: int, recipient_id: int, success_msg: str, response_type: str, data: dict):
        for socket in self._websockets[sender_id]:
            await socket.send_json(
                {
                    'type': 'SUCCESS',
                    'data': {'msg': success_msg},
                }
            )

        sockets = self._websockets[sender_id]
        if recipient_id in self._websockets.keys():
            sockets += self._websockets[recipient_id]

        for socket in sockets:
            await socket.send_json(
                {
                    'type': response_type,
                    'data': data,
                }
            )
