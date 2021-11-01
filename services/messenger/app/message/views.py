from fastapi import WebSocket


class WebSocketState:
    def __init__(self):
        self._websockets: dict[int, list[WebSocket]] = {}

    def add(self, user_id: int, websocket: WebSocket):
        if user_id not in self._websockets.keys():
            self._websockets[user_id] = []
        self._websockets[user_id].append(websocket)

    async def leave(self, user_id: int, websocket: WebSocket):
        if user_id not in self._websockets.keys():
            pass

        for index in range(len(self._websockets[user_id])):
            if self._websockets[user_id][index] == websocket:
                await self._websockets[user_id][index].close()
                del self._websockets[user_id][index]
                break
