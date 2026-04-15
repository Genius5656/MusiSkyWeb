from sqlalchemy import event
from sqlalchemy.sql import func, select
from sqlalchemy.orm import Session
from urllib.parse import unquote
from app.tracks.models import Tracks
from app.playlists.models import Playlists
from app.tracks_playlists.models import TracksPlaylists
from app.users_playlists.models import UsersPlaylists
import os


def _delete_file(file_url):
    """Удаление файла по URL"""
    if not file_url:
        return
    
    try:
        file_path = unquote(file_url)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ File deleted: {file_path}")
        else:
            print(f"⚠️ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error deleting file {file_url}: {e}")


@event.listens_for(TracksPlaylists, 'after_delete')
def delete_orphan_track(mapper, connection, target):
    """Удаление осиротевших треков"""
    
    result = connection.execute(
        select(func.count())
        .select_from(TracksPlaylists)
        .where(TracksPlaylists.track_id == target.track_id)
    )
    count = result.scalar()
    
    if count == 0:
        
        # Удаляем через ORM
        session = Session(bind=connection)
        track = session.get(Tracks, target.track_id)
        
        if track:
            track_url = track.track_url
            img_url = track.img_url
            
            session.delete(track)
            session.commit()
            
            # Удаляем файлы после успешного удаления из БД
            _delete_file(track_url)
            _delete_file(img_url)
        
        session.close()


@event.listens_for(UsersPlaylists, 'after_delete')
def delete_orphan_playlist(mapper, connection, target):
    """Удаление осиротевших плейлистов"""
    
    result = connection.execute(
        select(func.count())
        .select_from(UsersPlaylists)
        .where(UsersPlaylists.playlist_id == target.playlist_id)
    )
    count = result.scalar()
    
    if count == 0:
        
        # Удаляем через ORM
        session = Session(bind=connection)
        playlist = session.get(Playlists, target.playlist_id)
        
        if playlist:
            img_url = playlist.img_url
            
            session.delete(playlist)
            session.commit()
            
            # Удаляем обложку
            _delete_file(img_url)
        
        session.close()


@event.listens_for(Playlists, 'after_delete')
def delete_playlist_files(mapper, connection, target):
    """
    Дополнительный обработчик на случай прямого удаления Playlists.
    Удаляет файл обложки, если он есть.
    """
    if target.img_url:
        _delete_file(target.img_url)


@event.listens_for(Tracks, 'after_delete')
def delete_track_files(mapper, connection, target):
    """
    Дополнительный обработчик на случай прямого удаления Tracks.
    Удаляет файлы трека, если они есть.
    """
    if target.track_url:
        _delete_file(target.track_url)
    if target.img_url:
        _delete_file(target.img_url)
