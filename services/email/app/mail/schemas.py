from pydantic import BaseModel, EmailStr


class SendData(BaseModel):
    """ Send data """

    recipient: EmailStr
    subject: str
    template: str
    data: dict
    token: str
    user_id: int
