from fastapi import FastAPI, Query, HTTPException, APIRouter, Depends
from app.tracks_playlists.dao import TracksPlaylistsDAO
from fastapi.responses import JSONResponse
from app.tracks.dao import TracksDAO
from app.playlists.dao import PlaylistsDAO
from app.users_playlists.dao import UsersPlaylistsDAO
from app.youtube.schemas import SearchResponse, ChartsResponse, TrackInfo, PlaylistInfo, AlbumInfo, \
    ArtistInfo, YTTrackCreate, YTPlaylistCreate
from app.youtube.yt_interaction import get_audio_url, search_all_categories, get_track_details, \
    get_playlist_details, get_album_details, get_artist_details, get_charts_data, get_charts_by_category
from app.youtube.initialisation import ytmusic, logger
from app.users.dependensies import get_current_user
from app.users.models import User


# Настройка логирования
""" logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) """

router = APIRouter(prefix='/youtube', tags=['Youtube'])

""" try:
    ytmusic = YTMusic()
except Exception as e:
    logger.error(f"Ошибка инициализации YTMusic: {e}")
    ytmusic = None """


# --- Эндпоинт FastAPI ---

@router.get("/search", response_model=SearchResponse)
async def search_endpoint(
    q: str = Query(..., min_length=1, description="Поисковый запрос (название трека, исполнитель, альбом и т.д.)")
):
    """
    Асинхронно ищет треки, альбомы и исполнителей по заданному запросу.
    Возвращает структурированный словарь с результатами.
    """
    search_data = await search_all_categories(q)
    
    # Убедимся, что все ключи присутствуют, и присвоим None если списки пусты
    # (Pydantic с `Optional[List]` и `default_factory=list` сам обработает это элегантно)
    return SearchResponse(
        tracks=search_data["tracks"] or None,
        playlists=search_data["playlists"] or None,
        albums=search_data["albums"] or None,
        artists=search_data["artists"] or None
    )


@router.get("/track/{track_id}", response_model=TrackInfo)
async def get_track(track_id: str):
    """
    Получает детальную информацию о треке по его YouTube ID.
    Включает ссылку для прослушивания (audio_url) для вставки в JS плеер.
    
    Пример: GET /track/dQw4w9WgXcQ
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")
    
    track_info = await get_track_details(track_id)
    
    # Получаем ссылку на аудио
    # ВНИМАНИЕ: Это может занять некоторое время. Для продакшена лучше кэшировать результат
    audio_url = await get_audio_url(track_id)
    track_info.audio_url = audio_url
    
    return track_info


@router.get("/playlist/{playlist_id}", response_model=PlaylistInfo)
async def get_playlist(playlist_id: str):
    """
    Получает детальную информацию об альбоме и список его треков.
    
    Пример: GET /playlist/MPREb_ABC123
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")
    
    playlist_info = await get_playlist_details(playlist_id)
    return playlist_info


@router.get("/album/{album_id}", response_model=AlbumInfo)
async def get_album(album_id: str):
    """
    Получает детальную информацию об альбоме и список его треков.
    
    Пример: GET /album/MPREb_ABC123
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")
    
    album_info = await get_album_details(album_id)
    return album_info


@router.get("/artist/{artist_id}", response_model=ArtistInfo)
async def get_artist(artist_id: str):
    """
    Получает детальную информацию об исполнителе, включая:
    - Популярные треки
    - Альбомы
    - Синглы
    
    Пример: GET /artist/UCBR8-60-B28hp2BmDPdntcQ
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")
    
    artist_info = await get_artist_details(artist_id)
    return artist_info


@router.get("/charts", response_model=ChartsResponse)
async def get_charts(
    country: str = Query("RU", min_length=2, max_length=2, description="Код страны (RU, US, GB, DE и т.д.)"),
    limit: int = Query(50, ge=10, le=100, description="Количество треков в чарте")
):
    """
    Возвращает актуальные чарты YouTube Music для указанной страны.
    
    Доступные коды стран:
    - RU: Россия
    - US: США
    - GB: Великобритания
    - DE: Германия
    - FR: Франция
    - JP: Япония
    - KR: Южная Корея
    - GLOBAL: Мировой чарт
    
    Примеры:
    - GET /charts?country=RU&limit=20
    - GET /charts?country=US&limit=50
    - GET /charts?country=GLOBAL
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")
    
    try:
        charts_data = await get_charts_data(country.upper())
        
        # Ограничиваем количество результатов
        if charts_data["tracks"] and len(charts_data["tracks"]) > limit:
            charts_data["tracks"] = charts_data["tracks"][:limit]
        
        return ChartsResponse(
            country=charts_data["country"],
            updated=charts_data["updated"],
            tracks=charts_data["tracks"] if charts_data["tracks"] else None,
            artists=charts_data["artists"] if charts_data["artists"] else None
        )
        
    except Exception as e:
        logger.error(f"Ошибка в эндпоинте /charts: {e}")
        # Fallback: используем поиск по популярным трекам
        fallback_data = await get_charts_by_category("trending")
        
        if fallback_data["tracks"] and len(fallback_data["tracks"]) > limit:
            fallback_data["tracks"] = fallback_data["tracks"][:limit]
        
        return ChartsResponse(
            country="FALLBACK",
            updated=fallback_data["updated"],
            tracks=fallback_data["tracks"] if fallback_data["tracks"] else None,
            artists=fallback_data["artists"] if fallback_data["artists"] else None
        )


@router.get("/charts/{category}", response_model=ChartsResponse)
async def get_charts_by_type(
    category: str,
    limit: int = Query(50, ge=10, le=100)
):
    """
    Альтернативный эндпоинт для получения чартов по категориям.
    
    Доступные категории:
    - trending: Популярное сейчас
    - new: Новинки
    - top: Топ 100
    
    Пример: GET /charts/trending?limit=30
    """
    if ytmusic is None:
        raise HTTPException(status_code=503, detail="Сервис YTMusic не инициализирован")
    
    valid_categories = ["trending", "new", "top"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400, 
            detail=f"Недопустимая категория. Доступны: {', '.join(valid_categories)}"
        )
    
    charts_data = await get_charts_by_category(category)
    
    if charts_data["tracks"] and len(charts_data["tracks"]) > limit:
        charts_data["tracks"] = charts_data["tracks"][:limit]
    
    return ChartsResponse(
        country=charts_data["country"],
        updated=charts_data["updated"],
        tracks=charts_data["tracks"] if charts_data["tracks"] else None,
        artists=charts_data["artists"] if charts_data["artists"] else None
    )


@router.post("/addYTtrack")
async def add_track_playlist(data: YTTrackCreate):
    """Эндпоинт для добавления трека в плейлист"""

    track_data = {
        'yt_id': data.track_id,
        'img_url': data.cover_url,
        'title': data.title,
        'artist': data.artist,
        'album': data.album
    }

    track = await TracksDAO.add(**track_data)
    track_playlist_all = await TracksPlaylistsDAO.find_all(playlist_id=data.playlist_id)
    position = len(track_playlist_all) + 1

    tp_data = {
        'track_id': track.id,
        'playlist_id': data.playlist_id,
        'position': position
    }

    track_playlist = await TracksPlaylistsDAO.add(**tp_data)
    return JSONResponse(
        status_code=200,
        content={
            'message': 'TrackPlaylist added successfully',
            'playlist_id': track_playlist.playlist_id,
            'track_id': track_playlist.track_id,
            'position': position
        }
    )


@router.post("/addYTplaylist")
async def add_user_playlist(data: YTPlaylistCreate, current_user: User = Depends(get_current_user)):
    """Эндпоинт для добавления плейлиста пользователю"""

    playlist_data = {
        'yt_id': data.playlist_id,
        'author_id': 2,
        'title': data.title,
        'img_url': data.cover_url,
        'privacy': False
    }

    playlist = await PlaylistsDAO.add(**playlist_data)
    user_playlist_all = await UsersPlaylistsDAO.find_all(user_id=current_user.id)
    position = len(user_playlist_all) + 1

    up_data = {
        'playlist_id': playlist.id,
        'user_id': current_user.id,
        'position': position
    }

    user_playlist = await UsersPlaylistsDAO.add(**up_data)
    return JSONResponse(
        status_code=200,
        content={
            'message': 'UserPlaylist added successfully',
            'playlist_id': user_playlist.playlist_id,
            'user_id': user_playlist.user_id,
            'position': position
        }
    )