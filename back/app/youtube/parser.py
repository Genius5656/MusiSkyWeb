from typing import List, Dict, Optional
from app.youtube.schemas import TrackInfo, PlaylistInfo, AlbumInfo, ArtistInfo, ChartItem
from app.youtube.router import logger


def extract_thumbnails(thumbnails: List[Dict]) -> Optional[str]:
    """Извлекает URL обложки наилучшего качества."""
    if not thumbnails:
        return None
    # Обычно последний элемент в списке имеет самое высокое разрешение
    return thumbnails[-1].get('url')


def parse_track_result(item: Dict) -> TrackInfo:
    """Парсит результат поиска трека."""
    try:
        # Для треков идентификатор хранится в videoId
        track_id = item.get('videoId')
        # Если track_id отсутствует, возможно, элемент не доступен
        if not track_id:
            return None
            
        artists = item.get('artists', [])
        first_artist = artists[0] if artists else {}
        album = item.get('album')
        
        return TrackInfo(
            title=item.get('title'),
            track_id=track_id,
            cover_url=extract_thumbnails(item.get('thumbnails', [])),
            album=album.get('name') if album else None,
            album_id=album.get('id') if album else None,
            artist=first_artist.get('name'),
            artist_id=first_artist.get('id'),
            duration=item.get('duration_seconds')
        )
    except Exception as e:
        logger.warning(f"Ошибка парсинга трека: {e}, элемент: {item}")
        return None


def parse_playlist_result(item: Dict) -> PlaylistInfo:
    """Парсит результат поиска плейлиста."""
    try:
        playlist_id = item.get('browseId')
        if not playlist_id:
            return None
            
        return PlaylistInfo(
            title=item.get("title"),
            playlist_id=playlist_id,
            cover_url=extract_thumbnails(item.get('thumbnails', []))
        )
    except Exception as e:
        logger.warning(f"Ошибка парсинга исполнителя: {e}, элемент: {item}")
        return None


def parse_album_result(item: Dict) -> AlbumInfo:
    """Парсит результат поиска альбома."""
    try:
        album_id = item.get('browseId')
        if not album_id:
            return None
            
        artists = item.get('artists', [])
        first_artist = artists[0] if artists else {}
        
        return AlbumInfo(
            title=item.get('title'),
            album_id=album_id,
            cover_url=extract_thumbnails(item.get('thumbnails', [])),
            artist=first_artist.get('name'),
            artist_id=first_artist.get('id'),
            year=item.get('year'),
            type=item.get('type')
        )
    except Exception as e:
        logger.warning(f"Ошибка парсинга альбома: {e}, элемент: {item}")
        return None


def parse_artist_result(item: Dict) -> ArtistInfo:
    """Парсит результат поиска исполнителя."""
    try:
        artist_id = item.get('browseId')
        if not artist_id:
            return None
            
        return ArtistInfo(
            name=item.get('artist'),
            artist_id=artist_id,
            cover_url=extract_thumbnails(item.get('thumbnails', [])),
            subscribers=item.get('subscribers')
        )
    except Exception as e:
        logger.warning(f"Ошибка парсинга исполнителя: {e}, элемент: {item}")
        return None