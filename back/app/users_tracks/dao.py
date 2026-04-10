from app.dao.base import BaseDAO
from app.users_tracks.models import UsersTracks


class UsersTracksDAO(BaseDAO):
    model = UsersTracks