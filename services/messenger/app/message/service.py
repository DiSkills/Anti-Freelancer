from fastapi import WebSocket


async def websocket_error(websocket: WebSocket, detail: dict):
    await websocket.send_json(
        {
            'type': 'ERROR',
            'data': {'detail': detail}
        }
    )
