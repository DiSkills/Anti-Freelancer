from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.message.middleware import WebSocketStateMiddleware
from app.message.routers import message_router
from config import PROJECT_NAME, API

app = FastAPI(
    title=PROJECT_NAME,
    version='0.1.0',
    description='Messenger Service Anti-Freelancer by Counter',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(WebSocketStateMiddleware)


app.include_router(message_router, prefix=f'/{API}')