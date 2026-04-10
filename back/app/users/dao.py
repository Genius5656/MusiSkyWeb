from app.dao.base import BaseDAO
from app.users.models import User, BanList


class UsersDAO(BaseDAO):
    model = User

class BanListDAO(BaseDAO):
    model = BanList