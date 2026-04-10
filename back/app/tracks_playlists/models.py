from sqlalchemy import String, Integer, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.tracks.models import Tracks
from sqlalchemy.sql import func, select
from urllib.parse import unquote
import os


class TracksPlaylists(Base):
    __tablename__ = 'tracks_playlists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tracks.id", ondelete="CASCADE"), 
        nullable=False
    )
    playlist_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("playlists.id", ondelete="CASCADE"), 
        nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)


@event.listens_for(TracksPlaylists, 'after_delete')
def delete_orphan_track(mapper, connection, target):
    """
    Проверяет, остались ли другие связи с треком после удаления записи TracksPlaylists.
    Если связей нет - удаляет сам трек и связанный с ним файл.
    """
    # Проверяем, есть ли еще записи с таким track_id
    result = connection.execute(
        select(func.count())
        .select_from(TracksPlaylists)
        .where(TracksPlaylists.track_id == target.track_id)
    )
    count = result.scalar()
    
    # Если связей больше нет, получаем информацию о треке и удаляем его
    if count == 0:
        # Получаем данные трека перед удалением
        track_result = connection.execute(
            select(Tracks.track_url, Tracks.img_url, Tracks.id)
            .where(Tracks.id == target.track_id)
        )
        track_data = track_result.first()
        
        if track_data:
            track_url, img_url, track_id = track_data
            
            # Удаляем запись трека из БД
            connection.execute(
                Tracks.__table__.delete().where(Tracks.id == target.track_id)
            )
            
            # Удаляем файл трека, если путь существует
            if track_url:
                try:
                    # Декодируем URL-encoded путь
                    file_path = unquote(track_url)
                    
                    # Проверяем существование файла и удаляем
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        # Опционально: логируем успешное удаление
                        print(f"File deleted: {file_path}")
                    else:
                        print(f"File not found: {file_path}")
                        
                except Exception as e:
                    # Логируем ошибку, но не прерываем транзакцию
                    print(f"Error deleting file {track_url}: {str(e)}")
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