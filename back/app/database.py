from sqlalchemy import func, event
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

database_url = 'sqlite+aiosqlite:///db.sqlite3'

""" engine = create_async_engine(url=database_url) """
# Создаем движок с NullPool для SQLite
engine = create_async_engine(
    database_url, 
    poolclass=NullPool,  # Рекомендуется для SQLite
    echo=True
)

@event.listens_for(engine.sync_engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()

async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())