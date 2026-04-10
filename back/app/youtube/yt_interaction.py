import asyncio
from typing import Dict, Optional, Any
from fastapi import FastAPI, Query, HTTPException
from app.youtube.schemas import TrackInfo, PlaylistInfo, AlbumInfo, ArtistInfo, ChartItem
from app.youtube.parser import extract_thumbnails, parse_track_result, parse_playlist_result, \
    parse_album_result, parse_artist_result
from app.youtube.initialisation import ytmusic, logger
from datetime import datetime
import yt_dlp


async def get_audio_url(video_id: str) -> Optional[str]:
    """
    Получает прямую ссылку на аудиофайл для вставки в JS плеер.
    ВНИМАНИЕ: Это упрощенный пример. В реальном приложении нужно:
    1. Использовать библиотеку yt-dlp или youtube_dl асинхронно
    2. Кэшировать ссылки (они имеют ограниченное время жизни)
    3. Учитывать правовые аспекты
    """
    try:
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }
        
        def extract_info():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                url = f"https://www.youtube.com/watch?v={video_id}"
                info = ydl.extract_info(url, download=False)
                return info.get('url')
        
        # Выполняем в отдельном потоке
        audio_url = await asyncio.to_thread(extract_info)
        return audio_url
        
    except Exception as e:
        logger.error(f"Ошибка получения аудио URL для {video_id}: {e}")
        return None


async def search_all_categories(query: str) -> Dict[str, Any]:
    """
    Выполняет поиск по всем категориям и агрегирует результаты.
    ytmusicapi не поддерживает асинхронность из коробки, поэтому используем asyncio.to_thread.
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")

    try:
        # Выполняем синхронный поиск в отдельном потоке, чтобы не блокировать event loop
        raw_results = await asyncio.to_thread(ytmusic.search, query, filter="songs")
        logger.info(f"Поиск треков: найдено {len(raw_results)} результатов")
        
        tracks = []
        for item in raw_results:
            track_info = parse_track_result(item)
            if track_info:
                tracks.append(track_info)
        
        # Поиск плейлистов
        raw_playlists = await asyncio.to_thread(ytmusic.search, query, filter="playlists")
        logger.info(f"Поиск плейлистов: найдено {len(raw_playlists)} результатов")
        playlists = []
        for item in raw_playlists:
            playlist_info = parse_playlist_result(item)
            if playlist_info:
                playlists.append(playlist_info)

        # Поиск альбомов
        raw_albums = await asyncio.to_thread(ytmusic.search, query, filter="albums")
        logger.info(f"Поиск альбомов: найдено {len(raw_albums)} результатов")
        albums = []
        for item in raw_albums:
            album_info = parse_album_result(item)
            if album_info:
                albums.append(album_info)

        # Поиск исполнителей
        raw_artists = await asyncio.to_thread(ytmusic.search, query, filter="artists")
        logger.info(f"Поиск исполнителей: найдено {len(raw_artists)} результатов")
        artists = []
        for item in raw_artists:
            artist_info = parse_artist_result(item)
            if artist_info:
                artists.append(artist_info)

        return {
            "tracks": tracks,
            "playlists": playlists,
            "albums": albums,
            "artists": artists
        }
    except Exception as e:
        logger.error(f"Ошибка во время поиска: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении поиска: {str(e)}")


async def get_track_details(track_id: str) -> TrackInfo:
    """Получает детальную информацию о треке."""
    try:
        raw_info = await asyncio.to_thread(ytmusic.get_song, track_id)
        
        if not raw_info:
            raise HTTPException(status_code=404, detail="Трек не найден")
        
        video_details = raw_info.get('videoDetails', {})
        microformat = raw_info.get('microformat', {}).get('microformatDataRenderer', {})
        
        # Получаем информацию об альбоме
        album_info = None
        album_id = None
        if 'album' in microformat:
            album_info = microformat['album'].get('name')
            album_id = microformat['album'].get('id')
        
        # Получаем информацию об исполнителе
        artist_name = video_details.get('author')
        artist_id = video_details.get('channelId')
        
        track_info = TrackInfo(
            title=video_details.get('title'),
            track_id=video_details.get('videoId'),
            cover_url=extract_thumbnails(video_details.get('thumbnail', {}).get('thumbnails', [])),
            album=album_info,
            album_id=album_id,
            artist=artist_name,
            artist_id=artist_id,
            duration=int(video_details.get('lengthSeconds', 0)),
            audio_url=None  # Заполним отдельно
        )
        
        return track_info
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей трека {track_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации о треке: {str(e)}")


async def get_playlist_details(playlist_id: str) -> PlaylistInfo:
    """Получает детальную информацию об плейлисте и список треков."""
    try:
        raw_info = await asyncio.to_thread(ytmusic.get_playlist, playlist_id)
        
        if not raw_info:
            raise HTTPException(status_code=404, detail="Альбом не найден")
        
        playlist_info = PlaylistInfo(
            title=raw_info.get('title'),
            album_id=playlist_id,
            cover_url=extract_thumbnails(raw_info.get('thumbnails', [])),
            track_count=raw_info.get('trackCount'),
            duration=raw_info.get('duration'),
            tracks=[]
        )
        
        # Парсим треки альбома
        tracks = []
        for track_data in raw_info.get('tracks', []):
            # Информация об альбоме
            album = None
            album_id = None
            if "album" in track_data and track_data["album"]:
                album = track_data["album"].get("name")
                album_id = track_data["album"].get("id")
            
            # Информация об артистах
            artist = None
            artist_id = None
            artists = track_data.get("artists")
            if artists and len(artists) > 0:
                # Берем первого артиста как основного
                first_artist = artists[0]
                artist = first_artist.get("name")
                artist_id = first_artist.get("id")
                
                # Если артистов несколько, можно объединить их имена через запятую
                if len(artists) > 1:
                    all_artists = [a.get("name") for a in artists if a.get("name")]
                    if all_artists:
                        artist = ", ".join(all_artists)

            track_info = TrackInfo(
                title=track_data.get('title'),
                track_id=track_data.get('videoId'),
                cover_url=extract_thumbnails(track_data.get('thumbnails', [])),  # обложка альбома
                album=album,
                album_id=album_id,
                artist=artist,
                artist_id=artist_id,
                duration=int(track_data.get('duration_seconds', 0)) if track_data.get('duration_seconds') else None,
                audio_url=None
            )
            tracks.append(track_info)
        
        playlist_info.tracks = tracks if tracks else None
        return playlist_info
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей плейлиста {playlist_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации об альбоме: {str(e)}")


async def get_album_details(album_id: str) -> AlbumInfo:
    """Получает детальную информацию об альбоме и список треков."""
    try:
        raw_info = await asyncio.to_thread(ytmusic.get_album, album_id)
        
        if not raw_info:
            raise HTTPException(status_code=404, detail="Альбом не найден")
        
        # Парсим информацию об альбоме
        artists = raw_info.get('artists', [])
        first_artist = artists[0] if artists else {}
        
        album_info = AlbumInfo(
            title=raw_info.get('title'),
            album_id=album_id,
            cover_url=extract_thumbnails(raw_info.get('thumbnails', [])),
            artist=first_artist.get('name'),
            artist_id=first_artist.get('id'),
            year=raw_info.get('year'),
            type=raw_info.get('type'),
            track_count=raw_info.get('trackCount'),
            duration=raw_info.get('duration'),
            tracks=[]
        )
        
        # Парсим треки альбома
        tracks = []
        for track_data in raw_info.get('tracks', []):
            track_info = TrackInfo(
                title=track_data.get('title'),
                track_id=track_data.get('videoId'),
                cover_url=extract_thumbnails(raw_info.get('thumbnails', [])),  # обложка альбома
                album=raw_info.get('title'),
                album_id=album_id,
                artist=', '.join([artist.get('name', '') for artist in track_data.get('artists', [])]),
                artist_id=first_artist.get('id'),
                duration=int(track_data.get('duration_seconds', 0)) if track_data.get('duration_seconds') else None,
                audio_url=None
            )
            tracks.append(track_info)
        
        album_info.tracks = tracks if tracks else None
        return album_info
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей альбома {album_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации об альбоме: {str(e)}")


async def get_artist_details(artist_id: str) -> ArtistInfo:
    """Получает детальную информацию об исполнителе, включая популярные треки и альбомы."""
    try:
        raw_info = await asyncio.to_thread(ytmusic.get_artist, artist_id)
        
        if not raw_info:
            raise HTTPException(status_code=404, detail="Исполнитель не найден")
        
        # Парсим информацию об исполнителе
        header = raw_info.get('header', {})
        artist_info = ArtistInfo(
            name=raw_info.get('name'),
            artist_id=artist_id,
            cover_url=extract_thumbnails(raw_info.get('thumbnails', [])),
            subscribers=header.get('subscriberCountText', {}).get('text'),
            description=raw_info.get('description'),
            songs=[],
            albums=[],
            singles=[]
        )
        
        # Парсим популярные треки
        if 'songs' in raw_info and 'results' in raw_info['songs']:
            songs = []
            for track_data in raw_info['songs']['results'][:10]:  # ограничим до 10 треков
                album_data = track_data.get('album', {})
                track_info = TrackInfo(
                    title=track_data.get('title'),
                    track_id=track_data.get('videoId'),
                    cover_url=extract_thumbnails(track_data.get('thumbnails', [])),
                    album=album_data.get('name'),
                    album_id=album_data.get('id'),
                    artist=raw_info.get('name'),
                    artist_id=artist_id,
                    duration=int(track_data.get('duration_seconds', 0)) if track_data.get('duration_seconds') else None,
                    audio_url=None
                )
                songs.append(track_info)
            artist_info.songs = songs if songs else None
        
        # Парсим альбомы
        if 'albums' in raw_info and 'results' in raw_info['albums']:
            albums = []
            for album_data in raw_info['albums']['results']:
                album_info = AlbumInfo(
                    title=album_data.get('title'),
                    album_id=album_data.get('browseId'),
                    cover_url=extract_thumbnails(album_data.get('thumbnails', [])),
                    artist=raw_info.get('name'),
                    artist_id=artist_id,
                    year=album_data.get('year'),
                    type=album_data.get('type'),
                    tracks=None  # Не загружаем треки для экономии
                )
                if album_data.get('type') == 'Album':
                    albums.append(album_info)
            artist_info.albums = albums if albums else None
        
        # Парсим синглы
        if 'singles' in raw_info and 'results' in raw_info['singles']:
            singles = []
            for single_data in raw_info['singles']['results']:
                single_info = AlbumInfo(
                    title=single_data.get('title'),
                    album_id=single_data.get('browseId'),
                    cover_url=extract_thumbnails(single_data.get('thumbnails', [])),
                    artist=raw_info.get('name'),
                    artist_id=artist_id,
                    year=single_data.get('year'),
                    type='Single',
                    tracks=None
                )
                singles.append(single_info)
            artist_info.singles = singles if singles else None
        
        return artist_info
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей исполнителя {artist_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации об исполнителе: {str(e)}")
    

async def get_charts_data(country: str = "RU") -> Dict[str, Any]:
    """
    Получает данные чартов YouTube Music для указанной страны.
    
    Args:
        country: Двухбуквенный код страны (RU, US, GB, DE, FR, JP, KR и т.д.)
    """
    try:
        # Получаем чарты через ytmusicapi
        charts_data = await asyncio.to_thread(ytmusic.get_charts, country)
        
        result = {
            "country": country,
            "updated": charts_data.get('date'),
            "tracks": [],
            "artists": []
        }
        
        # Обрабатываем треки из чарта
        if 'items' in charts_data:
            for idx, item in enumerate(charts_data['items'][:50], 1):  # Топ-50 треков
                if item.get('videoId'):
                    # Базовая информация о треке
                    artists = item.get('artists', [])
                    first_artist = artists[0] if artists else {}
                    
                    track_info = TrackInfo(
                        title=item.get('title'),
                        track_id=item.get('videoId'),
                        cover_url=extract_thumbnails(item.get('thumbnails', [])),
                        album=item.get('album', {}).get('name') if isinstance(item.get('album'), dict) else None,
                        album_id=item.get('album', {}).get('id') if isinstance(item.get('album'), dict) else None,
                        artist=first_artist.get('name'),
                        artist_id=first_artist.get('id'),
                        duration=int(item.get('duration_seconds', 0)) if item.get('duration_seconds') else None,
                        isExplicit=item.get('isExplicit'),
                        audio_url=None  # Для чартов не получаем ссылки
                    )
                    
                    # Определяем тренд
                    trend = "steady"
                    if idx <= 10:
                        trend = "new" if item.get('isNew') else "steady"
                    
                    chart_item = ChartItem(
                        position=idx,
                        trend=trend,
                        views=item.get('views'),
                        track=track_info
                    )
                    
                    result["tracks"].append(chart_item)
        
        # Обрабатываем популярных исполнителей (если есть в ответе)
        if 'artists' in charts_data:
            for artist_data in charts_data['artists'].get('items', [])[:10]:  # Топ-10 исполнителей
                artist_info = ArtistInfo(
                    name=artist_data.get('title'),
                    artist_id=artist_data.get('browseId'),
                    cover_url=extract_thumbnails(artist_data.get('thumbnails', [])),
                    subscribers=artist_data.get('subscriberCount'),
                    description=None,
                    songs=None,
                    albums=None,
                    singles=None
                )
                result["artists"].append(artist_info)
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения чартов для страны {country}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения чартов: {str(e)}")


async def get_charts_by_category(category: str = "trending") -> Dict[str, Any]:
    """
    Альтернативный метод получения чартов по категориям через поиск.
    Используется если get_charts() недоступен или для дополнительных категорий.
    """
    try:
        category_map = {
            "trending": "популярное сейчас",
            "new": "новинки",
            "top": "топ 100"
        }
        
        search_query = category_map.get(category, "популярное сейчас")
        raw_results = await asyncio.to_thread(ytmusic.search, search_query, filter="songs", limit=50)
        
        result = {
            "country": "GLOBAL",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "tracks": [],
            "artists": []
        }
        
        for idx, item in enumerate(raw_results, 1):
            if item.get('videoId'):
                artists = item.get('artists', [])
                first_artist = artists[0] if artists else {}
                
                track_info = TrackInfo(
                    title=item.get('title'),
                    track_id=item.get('videoId'),
                    cover_url=extract_thumbnails(item.get('thumbnails', [])),
                    album=item.get('album', {}).get('name') if isinstance(item.get('album'), dict) else None,
                    album_id=item.get('album', {}).get('id') if isinstance(item.get('album'), dict) else None,
                    artist=first_artist.get('name'),
                    artist_id=first_artist.get('id'),
                    duration=int(item.get('duration_seconds', 0)) if item.get('duration_seconds') else None,
                    isExplicit=item.get('isExplicit'),
                    audio_url=None
                )
                
                chart_item = ChartItem(
                    position=idx,
                    trend="trending",
                    views=None,
                    track=track_info
                )
                
                result["tracks"].append(chart_item)
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения чартов по категории {category}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения чартов: {str(e)}")