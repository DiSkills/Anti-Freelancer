from pydantic import BaseModel


class GetClient(BaseModel):

    id: int
    secret: str
    client_name: str
