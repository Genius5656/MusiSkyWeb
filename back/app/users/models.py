from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import UsersPlaylists


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    playlists_associations: Mapped[list["UsersPlaylists"]] = relationship(
        "UsersPlaylists",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=False
    )

class BanList(Base):
    __tablename__ = 'banlist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # user_id: Mapped[int] = mapped_column(Integer, nullable=False,unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)