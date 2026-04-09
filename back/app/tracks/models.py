from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Tracks(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    yt_id: Mapped[str] = mapped_column(String, unique=True)
    track_url: Mapped[str] = mapped_column(String, unique=True)
    img_url: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    artist: Mapped[str] = mapped_column(String)
    album: Mapped[str] = mapped_column(String)
    views_all: Mapped[int] = mapped_column(String, nullable=False)
    views_date: Mapped[int] = mapped_column(String, nullable=False)
    """ privacy: Mapped[bool] = mapped_column(Boolean, nullable=False) """

