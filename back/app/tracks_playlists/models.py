from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import Playlists
    from app import Tracks


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

    playlist: Mapped["Playlists"] = relationship("Playlists", back_populates="tracks_associations")
    track: Mapped["Tracks"] = relationship("Tracks", back_populates="playlists_associations")