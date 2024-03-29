from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dialogue.routers import dialogues_router
from app.message.middleware import WebSocketStateMiddleware
from app.message.routers import message_router
from app.notification.routers import notification_router
from config import PROJECT_NAME, API, VERSION, CLIENT_NAME
from db import engine, Base

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description='Messenger Service Anti-Freelancer by Counter',
    root_path=f'/{CLIENT_NAME}',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(WebSocketStateMiddleware)


@app.on_event('startup')
async def startup():
    """ Startup """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

app.include_router(message_router, prefix=f'/{API}/messages')
app.include_router(notification_router, prefix=f'/{API}/notifications')
app.include_router(dialogues_router, prefix=f'/{API}/dialogues')
