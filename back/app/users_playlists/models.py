from sqlalchemy import String, Integer, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.playlists.models import Playlists
from sqlalchemy.sql import func, select
from urllib.parse import unquote
import os


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


@event.listens_for(UsersPlaylists, 'after_delete')
def delete_orphan_playlist(mapper, connection, target):
    """
    Этот обработчик синхронный и выполняется в контексте транзакции
    """
    result = connection.execute(
        select(func.count())
        .select_from(UsersPlaylists)
        .where(UsersPlaylists.playlist_id == target.playlist_id)
    )
    count = result.scalar()
    
    if count == 0:
        # Получаем данные трека перед удалением
        playlist_result = connection.execute(
            select(Playlists.img_url, Playlists.id)
            .where(Playlists.id == target.track_id)
        )
        playlist_data = playlist_result.first()

        if playlist_data:
            img_url, playlist_id = playlist_data

            connection.execute(
                Playlists.__table__.delete().where(Playlists.id == target.playlist_id)
            )

            # Удаляем файл обложки, если путь существует
            if img_url:
                try:
                    # Декодируем URL-encoded путь
                    file_path = unquote(img_url)
                    
                    # Проверяем существование файла и удаляем
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        # Опционально: логируем успешное удаление
                        print(f"File deleted: {file_path}")
                    else:
                        print(f"File not found: {file_path}")
                        
                except Exception as e:
                    # Логируем ошибку, но не прерываем транзакцию
                    print(f"Error deleting file {img_url}: {str(e)}")