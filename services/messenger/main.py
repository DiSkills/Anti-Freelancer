from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.message.middleware import WebSocketStateMiddleware
from config import PROJECT_NAME

app = FastAPI(
    title=PROJECT_NAME,
    version='0.2.0',
    description='Messenger Service Anti-Freelancer by Counter021',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(WebSocketStateMiddleware)
