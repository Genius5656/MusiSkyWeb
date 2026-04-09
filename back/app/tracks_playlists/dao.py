from app.dao.base import BaseDAO
from app.tracks_playlists.models import TracksPlaylists


class TracksPlaylistsDAO(BaseDAO):
    model = TracksPlaylists