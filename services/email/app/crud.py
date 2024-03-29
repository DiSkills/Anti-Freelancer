from app.models import Client
from crud import CRUD


class ClientCRUD(CRUD[Client, Client, Client]):
    """ Client CRUD """
    pass


client_crud = ClientCRUD(Client)
