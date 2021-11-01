from starlette.types import ASGIApp, Scope, Receive, Send

from app.message.views import WebSocketState


class WebSocketStateMiddleware:
    """ WebSocket state middleware """

    def __init__(self, app: ASGIApp):
        self._app = app
        self._state = WebSocketState()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] in ('lifespan', 'http', 'websocket'):
            scope['websockets'] = self._state
        await self._app(scope, receive, send)
