from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UsersTracks(Base):
    __tablename__ = 'users_tracks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    track_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tracks.id", ondelete="CASCADE"), 
        nullable=False
    )

