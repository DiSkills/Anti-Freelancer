from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.client.routers import client_router
from app.mail.routers import mail_router
from config import PROJECT_NAME, API, DOCKER
from db import engine, Base

app = FastAPI(
    title=PROJECT_NAME,
    version='0.1.0',
    description='Email Service Anti-Freelancer by Counter',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup():
    if int(DOCKER):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)


app.include_router(mail_router, prefix=f'/{API}')
app.include_router(client_router, prefix=f'/{API}/clients')
