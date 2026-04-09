from app.dao.base import BaseDAO
from app.tracks.models import Tracks


class TracksDAO(BaseDAO):
    model = Tracks