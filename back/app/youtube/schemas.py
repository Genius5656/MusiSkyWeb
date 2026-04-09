from typing import List, Optional
from pydantic import BaseModel, Field


class TrackInfo(BaseModel):
    title: Optional[str] = None
    track_id: Optional[str] = None
    cover_url: Optional[str] = None
    album: Optional[str] = None
    album_id: Optional[str] = None
    artist: Optional[str] = None
    artist_id: Optional[str] = None
    duration: Optional[int] = None
    # Новое поле для ссылки прослушивания (будет заполняться только в эндпоинте /track)
    audio_url: Optional[str] = None


class PlaylistInfo(BaseModel):
    title: Optional[str] = None
    playlist_id: Optional[str] = None
    cover_url: Optional[str] = None
    track_count: Optional[int] = None
    duration: Optional[str] = None
    tracks: Optional[List[TrackInfo]] = None


class AlbumInfo(BaseModel):
    title: Optional[str] = None
    album_id: Optional[str] = None
    cover_url: Optional[str] = None
    artist: Optional[str] = None
    artist_id: Optional[str] = None
    year: Optional[str] = None
    type: Optional[str] = None
    track_count: Optional[int] = None
    duration: Optional[str] = None  # общая длительность альбома
    # Новое поле для списка треков
    tracks: Optional[List[TrackInfo]] = None


class ArtistInfo(BaseModel):
    name: Optional[str] = None
    artist_id: Optional[str] = None
    cover_url: Optional[str] = None
    subscribers: Optional[str] = None
    description: Optional[str] = None
    # Новые поля для списков контента исполнителя
    songs: Optional[List[TrackInfo]] = None
    albums: Optional[List['AlbumInfo']] = None
    singles: Optional[List['AlbumInfo']] = None


class SearchResponse(BaseModel):
    tracks: Optional[List[TrackInfo]] = Field(default_factory=list)
    playlists: Optional[List[PlaylistInfo]] = Field(default_factory=list)
    artists: Optional[List[ArtistInfo]] = Field(default_factory=list)
    albums: Optional[List[AlbumInfo]] = Field(default_factory=list)


class ChartItem(BaseModel):
    """Модель для отдельного трека в чарте с позицией и статистикой."""
    position: Optional[int] = None
    trend: Optional[str] = None  # "up", "down", "new", "steady"
    views: Optional[str] = None
    track: Optional[TrackInfo] = None


class ChartsResponse(BaseModel):
    """Модель ответа для эндпоинта /charts."""
    country: Optional[str] = None
    updated: Optional[str] = None
    tracks: Optional[List[ChartItem]] = Field(default_factory=list)
    artists: Optional[List[ArtistInfo]] = Field(default_factory=list)


class YTTrackCreate(BaseModel):
    playlist_id: int
    track_id: str
    cover_url: Optional[str] = None
    title: str
    album: Optional[str] = None
    artist: Optional[str] = None
    duration: Optional[int] = None

