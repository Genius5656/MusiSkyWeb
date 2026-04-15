from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.database import Base
if TYPE_CHECKING:
    from app import User
    from app import Playlists


class UsersPlaylists(Base):
    __tablename__ = 'users_playlists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    playlist_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("playlists.id", ondelete="CASCADE"), 
        nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="playlists_associations")
    playlist: Mapped["Playlists"] = relationship("Playlists", back_populates="users_associations")