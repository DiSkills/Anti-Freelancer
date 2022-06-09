from pydantic import BaseModel, EmailStr


class SendData(BaseModel):
    """ Send data """

    recipient: EmailStr
    subject: str
    template: str
    data: dict

    secret: str
    client_name: str
