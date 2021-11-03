from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import notification_crud
from app.requests import get_users


async def get_notifications(db: AsyncSession, user_id: int):
    ids = await notification_crud.filter_ids(db, recipient_id=user_id)

    users = await get_users(ids)

    return (
        {
            **notification.__dict__,
            'data': {
                **notification.message.__dict__,
                'sender': users[f'{notification.sender_id}'],
            }
        } for notification in await notification_crud.filter(db, recipient_id=user_id)
    )
