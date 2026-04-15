from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
from app.exceptions import NoUserTrackException
from app.users_tracks.dao import UsersTracksDAO
from app.tracks.schemas import TracksRead
from app.tracks.dao import TracksDAO
from app.users.dependensies import get_current_user
from app import User

router = APIRouter(prefix='/users_tracks', tags=['UsersTracks'])


@router.get("/userTracks/tracks")
async def get_track_by_history(current_user: User = Depends(get_current_user)):
    """Получение прослушанных треков пользователем за неделю"""

    user_tracks = await UsersTracksDAO.find_all(user_id=current_user.id)
    if not user_tracks:
        raise NoUserTrackException
    
    week_ago = datetime.now() - timedelta(days=7)

    for user_track in user_tracks:
        if user_track.created_at < week_ago:
            await UsersTracksDAO.delete(user_track.id)
    
    # Получаем записи за неделю через UsersTracksDAO
    recent_listens = await UsersTracksDAO.find_all(user_id=current_user.id)
    
    # Фильтруем только за неделю (на случай если есть записи без точного фильтра)
    recent_listens = [
        listen for listen in recent_listens 
        if listen.created_at >= week_ago
    ]
    
    # Получаем данные треков и группируем по датам
    grouped_tracks = defaultdict(list)

    for listen in recent_listens:
        track = await TracksDAO.find_one_or_none_by_id(listen.track_id)
        if track:
            date_key = listen.created_at.strftime("%d.%m.%Y")
            track_data = TracksRead.model_validate(track).model_dump()
            grouped_tracks[date_key].append(track_data)
        
    return dict(grouped_tracks)


@router.post("/addUserTrack")
async def add_user_track(track_id: int, current_user: User = Depends(get_current_user)):
    """Эндпоинт для загрузки и обработки MP3 файла"""
    
    ut_data = {
        'user_id': current_user.id,
        'track_id': track_id,
        'views': 0
    }

    user_track = await UsersTracksDAO.add(**ut_data)

    return JSONResponse(
        status_code=200,
        content={
            'message': 'UserTrack added successfully',
            'track_id': user_track.track_id,
            'user_id': user_track.user_id,
        }
    )
