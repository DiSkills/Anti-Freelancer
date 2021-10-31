from fastapi import HTTPException, status

from app import requests


async def get_sender(sender_id: int) -> dict:
    """
        Get sender
        :param sender_id: Sender
        :type sender_id: int
        :return: User data
        :rtype: dict
    """
    try:
        response = await requests.get_user_request(sender_id)
    except ValueError as _ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_ex.args[0])
    else:
        return response


async def get_recipient(recipient_id: int) -> dict:
    """
        Get recipient
        :param recipient_id: Recipient
        :type recipient_id: int
        :return: User data
        :rtype: dict
    """
    try:
        response = await requests.get_user_request(recipient_id)
    except ValueError as _ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_ex.args[0])
    else:
        return response
