from app import requests


async def get_sender(sender_id: int) -> dict:
    """
        Get sender
        :param sender_id: Sender
        :type sender_id: int
        :return: User data
        :rtype: dict
    """
    return await requests.get_user_request(sender_id)


async def get_recipient(recipient_id: int) -> dict:
    """
        Get recipient
        :param recipient_id: Recipient
        :type recipient_id: int
        :return: User data
        :rtype: dict
    """
    return await requests.get_user_request(recipient_id)
