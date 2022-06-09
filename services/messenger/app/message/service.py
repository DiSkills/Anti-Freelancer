from fastapi import WebSocket

from config import ERROR


async def websocket_error(websocket: WebSocket, detail: dict) -> None:
    """
        Websocket error
        :param websocket: Websocket
        :type websocket: WebSocket
        :param detail: Detail
        :type detail: dict
        :return: None
    """
    await websocket.send_json(
        {
            'type': ERROR,
            'data': {'detail': detail}
        }
    )
