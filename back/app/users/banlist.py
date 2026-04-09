from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.dao.base import BaseDAO


class BanList(Base):
    __tablename__ = 'banlist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),  # Добавлен ondelete
        nullable=False,
        unique=True
    )

class BanListDAO(BaseDAO):
    model = BanList
