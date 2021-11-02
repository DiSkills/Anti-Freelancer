import os

import jwt
from fastapi import HTTPException, status

from app.mail.schemas import SendData
from config import TEST, SECRET_KEY
from tasks import send_email

ALGORITHM = 'HS256'


def verify_token(token: str) -> int:
    """
        Verify token
        :param token: Token
        :type token: str
        :return: User ID
        :rtype: int
        :raise HTTPException 400: Bad token
        :raise HTTPException 401: Token lifetime ended
        :raise HTTPException 403: Could not validate credentials
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded['sub'] != 'access':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad token')

        return decoded['user_id']
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token lifetime ended')
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials')


async def send(schema: SendData) -> dict[str, str]:
    """
        Send email
        :param schema: Send data
        :type schema: SendData
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Bad token
        :raise HTTPException 400: Template not found
    """
    if schema.user_id != verify_token(schema.token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad token')

    if not os.path.exists(f'templates/{schema.template}'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Template not found')

    if not int(TEST):
        send_email.delay(schema.recipient, schema.subject, f'templates/{schema.template}', **schema.data)
    return {'msg': 'Email has been send'}
