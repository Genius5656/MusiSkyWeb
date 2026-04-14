from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TracksPlaylists(Base):
    __tablename__ = 'tracks_playlists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tracks.id", ondelete="CASCADE"), 
        nullable=False
    )
    playlist_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("playlists.id", ondelete="CASCADE"), 
        nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
