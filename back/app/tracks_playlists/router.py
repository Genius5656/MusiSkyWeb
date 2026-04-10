from fastapi import FastAPI, HTTPException, APIRouter, Depends
from typing import List
from fastapi.responses import JSONResponse
from app.media_interaction import save_image, convert_image_to_bytes, delete_file_by_path
from app.exceptions import NoPlaylistException, NoTrackException, NoTrackPlaylistException
from app.tracks_playlists.dao import TracksPlaylistsDAO
from app.tracks.dao import TracksDAO
from app.playlists.dao import PlaylistsDAO
from app.tracks_playlists.schemas import TracksPlaylistsCreate, TracksPlaylistsRead, TracksPlaylistsUpdate, TracksPlaylistsDelete
from app.tracks.schemas import TracksRead

router = APIRouter(prefix='/tracks_playlists', tags=['TracksPlaylists'])


@router.get("/trackPlaylist/tracks/{playlist_id}", response_model=List[TracksRead])
async def get_tracks_by_playlist_id(playlist_id: int):
    """Эндпоинт для получения всех треков плейлиста"""

    track_playlist_all = await TracksPlaylistsDAO.find_all(playlist_id=playlist_id)
    sorted_tp_list = sorted(track_playlist_all, key=lambda trackPlaylist: trackPlaylist['position'])

    tracks_list = []
    for track_playlist in sorted_tp_list:
        track = await TracksDAO.find_one_or_none_by_id(track_playlist.track_id)
        tracks_list.append(track)
    
    return tracks_list


@router.post("/addTrackPlaylist")
async def add_track_playlist(data: TracksPlaylistsCreate):
    """Эндпоинт для добавления трека в плейлист"""

    if not(await PlaylistsDAO.find_one_or_none_by_id(data.playlist_id)):
        raise NoPlaylistException
    
    track = 1
    
    track_playlist_all = await TracksPlaylistsDAO.find_all(playlist_id=data.playlist_id)
    position = len(track_playlist_all) + 1
    
    track_playlist_data = {
        'track_id': track.id,
        'playlist_id': data.playlist_id,
        'position': position
    }

    track_playlist = await TracksPlaylistsDAO.add(**track_playlist_data)

    return JSONResponse(
        status_code=200,
        content={
            'message': 'TrackPlaylist added successfully',
            'playlist_id': track_playlist.playlist_id,
            'track_id': track.id,
            'position': position
        }
    )


@router.put("/updateTrackPosition")
async def update_tracks_position(data: TracksPlaylistsUpdate):
    """Эндпоинт для изменения позиции трека в плейлисте"""

    if not(await TracksDAO.find_one_or_none_by_id(data.track_id)):
        raise NoTrackException
    if not(await PlaylistsDAO.find_one_or_none_by_id(data.playlist_id)):
        raise NoPlaylistException

    tp_filter = {
        'track_id': data.track_id,
        'playlist_id': data.playlist_id
    }

    db_playlist_track = await TracksPlaylistsDAO.find_one_or_none(**tp_filter)
    all_playlist_tracks = await TracksPlaylistsDAO.find_all(playlist_id=data.playlist_id)

    old_pos = db_playlist_track.position
    new_pos = data.position

    try:
        if new_pos < old_pos:
            for playlist_track in all_playlist_tracks:
                if (playlist_track.position >= new_pos) and (playlist_track.position < old_pos):
                    track_playlist_update = await TracksPlaylistsDAO.update(playlist_track, {'postion': (playlist_track.position + 1)})
        else:
            for playlist_track in all_playlist_tracks:
                if (playlist_track.position > new_pos) and (playlist_track.position <= old_pos):
                    track_playlist_update = await TracksPlaylistsDAO.update(playlist_track, {'postion': (playlist_track.position - 1)})
                    
    except Exception as e:
        print(f"/updateTrackPosition Exception: {str(e)}")
        raise
    
    track_playlist = await TracksPlaylistsDAO.update(db_playlist_track, {'position': new_pos})

    return JSONResponse(
        status_code=200,
        content={
            'message': 'TrackPlaylist position updated successfully',
            'playlist_id': track_playlist.playlist_id,
            'track_id': track_playlist.track_id,
            'position': new_pos
        }
    )


# BAG
@router.delete("/deleteTrackPlaylist", response_model=TracksPlaylistsRead)
async def delete_track_playlist(data: TracksPlaylistsDelete):
    """Эндпоинт для удаления трека из плейлиста"""
    
    tp_filter = {
        'track_id': data.track_id,
        'playlist_id': data.playlist_id
    }

    track_playlist = await TracksPlaylistsDAO.find_one_or_none(**tp_filter)
    if not track_playlist:
        raise NoTrackPlaylistException

    return track_playlist
