from app.database import Base
from app.users.models import User, BanList
from app.playlists.models import Playlists
from app.tracks.models import Tracks
from app.users_playlists.models import UsersPlaylists
from app.tracks_playlists.models import TracksPlaylists
from app.users_tracks.models import UsersTracks

# ВАЖНО: импортируем события, чтобы они зарегистрировались
#from . import events  # или from .events import *
from app.events import *

__all__ = [
    "Base",
    "User",
    "Playlists",
    "Tracks",
    "UsersPlaylists",
    "TracksPlaylists",
    "BanList",
    "UsersTracks",
]