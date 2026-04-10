from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Tracks(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    yt_id: Mapped[str] = mapped_column(String)
    track_url: Mapped[str] = mapped_column(String)
    img_url: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    artist: Mapped[str] = mapped_column(String)
    album: Mapped[str] = mapped_column(String)
    """ views_all: Mapped[int] = mapped_column(String, nullable=False)
    views_date: Mapped[int] = mapped_column(String, nullable=False) """
    """ privacy: Mapped[bool] = mapped_column(Boolean, nullable=False) """

