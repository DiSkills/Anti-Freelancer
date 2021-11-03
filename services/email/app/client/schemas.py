from pydantic import BaseModel


class GetClient(BaseModel):
    """ Get client """

    id: int
    secret: str
    client_name: str
