from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from app import TracksPlaylists


class Tracks(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    yt_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    track_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    img_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    artist: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    album: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    """ views_all: Mapped[int] = mapped_column(String, nullable=False)
    views_date: Mapped[int] = mapped_column(String, nullable=False) """
    """ privacy: Mapped[bool] = mapped_column(Boolean, nullable=False) """

    playlists_associations: Mapped[list["TracksPlaylists"]] = relationship(
        "TracksPlaylists",
        back_populates="track",
        cascade="all, delete-orphan",
        passive_deletes=False
    )