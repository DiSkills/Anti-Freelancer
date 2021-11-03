from app.requests import get_user_data_and_server_token
from config import PROJECT_NAME, API, SERVER_MAIN_BACKEND, TEST
from send_email import send_email


async def send_select_email(user_id: int, job_id: int) -> None:
    """
        Send select executor email
        :param user_id: User ID
        :type user_id: int
        :param job_id: Job ID
        :type job_id: int
        :return: None
    """
    if int(TEST):
        return

    server_token, user_data = await get_user_data_and_server_token(user_id)
    await send_email(
        server_token,
        user_data['email'],
        f'Select email - {PROJECT_NAME}',
        'select.html',
        username=user_data['username'],
        link=f'{SERVER_MAIN_BACKEND}{API}/jobs/{job_id}',
    )
