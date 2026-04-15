from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
if TYPE_CHECKING:
    from app import TracksPlaylists
    from app import UsersPlaylists


class Playlists(Base):
    __tablename__ = 'playlists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    yt_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    author_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),  # Добавлен ondelete
        nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    privacy: Mapped[bool] = mapped_column(Boolean, nullable=False)

    tracks_associations: Mapped[list["TracksPlaylists"]] = relationship(
        "TracksPlaylists",
        back_populates="playlist",
        cascade="all, delete-orphan",
        passive_deletes=False
    )

    users_associations: Mapped[list["UsersPlaylists"]] = relationship(
        "UsersPlaylists",
        back_populates="playlist",
        cascade="all, delete-orphan",
        passive_deletes=False
    )