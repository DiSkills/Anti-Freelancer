from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

import views
from config import PROJECT_NAME
from schemas import Data, Message

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


@app.post(
    '/send',
    name='Send email',
    description='Send email',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['email'],
)
async def send(schema: Data):
    return await views.send(schema)
