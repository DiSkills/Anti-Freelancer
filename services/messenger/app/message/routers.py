from fastapi import APIRouter
from starlette.endpoints import WebSocketEndpoint

message_router = APIRouter()


@message_router.websocket_route('/ws/{token}')
class MessengerRouter(WebSocketEndpoint):
    pass
