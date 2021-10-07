import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import auth_router
from config import PROJECT_NAME, API, MEDIA_ROOT, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL
from createsuperuser import createsuperuser
from db import async_session

app = FastAPI(
    title=PROJECT_NAME,
    version='0.1.0',
    description='Auth Service Anti-Freelancer by Counter',
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
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)
    async with async_session() as session:
        await createsuperuser(session, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL)


@app.get(
    '/media/{directory}/{file_name}',
    name='Media',
    description='Get media files',
    response_description='File',
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    tags=['media'],
)
async def media(directory: str, file_name: str) -> FileResponse:
    """
        Media
        :param directory: Directory user
        :type directory: str
        :param file_name: File name
        :type file_name: str
        :return: File
        :rtype: FileResponse
        :raise HTTPException 404: File not found
    """

    if not os.path.exists(f'{MEDIA_ROOT}{directory}/{file_name}'):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')
    return FileResponse(f'{MEDIA_ROOT}{directory}/{file_name}', status_code=status.HTTP_200_OK)


app.include_router(auth_router, prefix=f'/{API}')
