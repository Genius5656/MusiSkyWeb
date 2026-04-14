from typing import Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


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