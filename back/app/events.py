from sqlalchemy import event
from app.playlists.models import Playlists
from sqlalchemy.sql import func, select
from urllib.parse import unquote
from app.tracks.models import Tracks
from app.tracks_playlists.models import TracksPlaylists
from app.users_playlists.models import UsersPlaylists
from app.users.models import User
import os


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
        # Получаем данные плейлиста перед удалением
        playlist_result = connection.execute(
            select(Playlists.img_url, Playlists.id)
            .where(Playlists.id == target.playlist_id)
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


@event.listens_for(User, 'after_delete')
def cleanup_orphan_playlists_after_user_delete(mapper, connection, target):
    """
    После удаления пользователя находим все плейлисты, которые потеряли все связи,
    удаляем их, что каскадно удалит TracksPlaylists, а затем треки-сироты.
    """
    # Находим плейлисты, у которых нет записей в UsersPlaylists
    orphan_playlists = connection.execute(
        select(Playlists.id, Playlists.img_url)
        .outerjoin(UsersPlaylists, Playlists.id == UsersPlaylists.playlist_id)
        .where(UsersPlaylists.id == None)
    ).fetchall()
    
    for playlist_id, img_url in orphan_playlists:
        # Удаляем запись плейлиста (это каскадно удалит связанные TracksPlaylists)
        connection.execute(
            Playlists.__table__.delete().where(Playlists.id == playlist_id)
        )
        
        # Удаляем файл обложки
        if img_url:
            try:
                file_path = unquote(img_url)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Playlist image deleted: {file_path}")
                else:
                    print(f"Playlist image not found: {file_path}")
            except Exception as e:
                print(f"Error deleting playlist image {img_url}: {str(e)}")


@event.listens_for(Playlists, 'after_delete')
def cleanup_orphan_tracks_after_playlist_delete(mapper, connection, target):
    """
    После удаления плейлиста (в том числе каскадного) находим треки-сироты и удаляем их.
    Это событие сработает как при прямом удалении плейлиста, так и при удалении через
    cleanup_orphan_playlists_after_user_delete.
    """
    # Находим треки, у которых нет записей в TracksPlaylists
    orphan_tracks = connection.execute(
        select(Tracks.id, Tracks.track_url, Tracks.img_url)
        .outerjoin(TracksPlaylists, Tracks.id == TracksPlaylists.track_id)
        .where(TracksPlaylists.id == None)
    ).fetchall()
    
    for track_id, track_url, img_url in orphan_tracks:
        # Удаляем запись трека
        connection.execute(
            Tracks.__table__.delete().where(Tracks.id == track_id)
        )
        
        # Удаляем файлы трека
        for file_url in (track_url, img_url):
            if file_url:
                try:
                    file_path = unquote(file_url)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Track file deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting track file {file_url}: {str(e)}")




""" @event.listens_for(Playlists, 'after_delete')
def cleanup_orphan_tracks_after_playlist_delete(mapper, connection, target):
    
    После удаления плейлиста находим все треки, которые потеряли все связи,
    и удаляем их вместе с файлами.
   
    # Находим треки, у которых нет записей в TracksPlaylists
    orphan_tracks = connection.execute(
        select(Tracks.id, Tracks.track_url, Tracks.img_url)
        .outerjoin(TracksPlaylists, Tracks.id == TracksPlaylists.track_id)
        .where(TracksPlaylists.id == None)
    ).fetchall()
    
    for track_id, track_url, img_url in orphan_tracks:
        # Удаляем запись трека
        connection.execute(
            Tracks.__table__.delete().where(Tracks.id == track_id)
        )
        
        # Удаляем файлы
        for file_url in (track_url, img_url):
            if file_url:
                try:
                    file_path = unquote(file_url)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"File deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_url}: {str(e)}") """