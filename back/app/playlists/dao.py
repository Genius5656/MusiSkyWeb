from app.dao.base import BaseDAO
from app.playlists.models import Playlists


class PlaylistsDAO(BaseDAO):
    model = Playlists