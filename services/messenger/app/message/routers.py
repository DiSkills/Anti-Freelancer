import typing

from fastapi import APIRouter, WebSocket
from starlette.endpoints import WebSocketEndpoint

from app.message import views
from app.message.state import WebSocketState

message_router = APIRouter()


@message_router.websocket_route('/ws/{token}')
class MessengerRouter(WebSocketEndpoint, views.MessengerView):

    async def on_connect(self, websocket: WebSocket) -> None:
        state: typing.Optional[WebSocketState] = self.scope.get('websockets')
        await self.connect(state, websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.disconnect(websocket)
