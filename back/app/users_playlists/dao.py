from app.dao.base import BaseDAO
from app.users_playlists.models import UsersPlaylists


class UsersPlaylistsDAO(BaseDAO):
    model = UsersPlaylists