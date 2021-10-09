import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from app.admin.routers import admin_router
from app.auth.routers import auth_router
from app.routers import permission_router
from app.skills.routers import skills_router
from config import PROJECT_NAME, API, MEDIA_ROOT, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL, SECRET_KEY
from createsuperuser import createsuperuser
from db import async_session

app = FastAPI(
    title=PROJECT_NAME,
    version='0.3.0',
    description='Auth Service Anti-Freelancer by Counter',
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

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


app.include_router(admin_router, prefix=f'/{API}/admin')
app.include_router(auth_router, prefix=f'/{API}')
app.include_router(permission_router, prefix=f'/{API}')
app.include_router(skills_router, prefix=f'/{API}/skills')
