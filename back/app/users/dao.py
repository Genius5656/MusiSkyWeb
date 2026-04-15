from app.dao.base import BaseDAO
from app import User, BanList


class UsersDAO(BaseDAO):
    model = User

class BanListDAO(BaseDAO):
    model = BanList