from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.responses import JSONResponse
from app.exceptions import NoPlaylistException, NoUserException, NoUserPlaylistException
from app.users_playlists.dao import UsersPlaylistsDAO
from app.users.dependensies import get_current_user
from app import User
from app.users.dao import UsersDAO
from app.playlists.dao import PlaylistsDAO
from app.users_playlists.schemas import UsersPlaylistsRead, UsersPlaylistsUpdate

router = APIRouter(prefix='/users_playlists', tags=['UsersPlaylists'])


@router.get("/userPlaylist/playlists")
async def get_playlists_by_user_id(current_user: User = Depends(get_current_user)):
    """Эндпоинт для получения всех плейлистов пользователя"""

    user_playlist_all = await UsersPlaylistsDAO.find_all(user_id=current_user.id)
    sorted_tp_list = sorted(user_playlist_all, key=lambda userPlaylist: userPlaylist.position)

    playlists_list = []
    for user_playlist in sorted_tp_list:
        playlist = await PlaylistsDAO.find_one_or_none_by_id(user_playlist.playlist_id)
        playlists_list.append(playlist)
    
    return playlists_list


@router.post("/addUserPlaylist")
async def add_user_playlist(title: str, current_user: User = Depends(get_current_user)):
    """Эндпоинт для добавления плейлиста пользователю"""
    
    playlist_data = {
        'yt_id': "",
        'author_id': current_user.id,
        'title': title,
        'img_url': "",
        'privacy': True
    }

    playlist = await PlaylistsDAO.add(**playlist_data)
    
    user_playlist_all = await UsersPlaylistsDAO.find_all(user_id=current_user.id)
    position = len(user_playlist_all) + 1
    
    user_playlist_data = {
        'user_id': current_user.id,
        'playlist_id': playlist.id,
        'position': position
    }

    user_playlist = await UsersPlaylistsDAO.add(**user_playlist_data)

    return JSONResponse(
        status_code=200,
        content={
            'message': 'UserPlaylist added successfully',
            'playlist_id': playlist.id,
            'user_id': user_playlist.user_id,
            'position': position
        }
    )


@router.put("/updatePlaylistsPosition")
async def update_playlists_position(data: UsersPlaylistsUpdate, current_user: User = Depends(get_current_user)):
    """Эндпоинт для изменения позиции плейлиста у пользователя"""

    if not(await UsersDAO.find_one_or_none_by_id(current_user.id)):
        raise NoUserException
    if not(await PlaylistsDAO.find_one_or_none_by_id(data.playlist_id)):
        raise NoPlaylistException

    up_filter = {
        'user_id': current_user.id,
        'playlist_id': data.playlist_id
    }

    db_playlist_user = await UsersPlaylistsDAO.find_one_or_none(**up_filter)
    all_playlist_users = await UsersPlaylistsDAO.find_all(user_id=current_user.id)

    old_pos = db_playlist_user.position
    new_pos = data.position
    print(old_pos)
    print(new_pos)

    try:
        if new_pos < old_pos:
            for playlist_user in all_playlist_users:
                if (playlist_user.position >= new_pos) and (playlist_user.position < old_pos):
                    await UsersPlaylistsDAO.update(playlist_user, {'position': playlist_user.position + 1})
        else:
            for playlist_user in all_playlist_users:
                if (playlist_user.position > old_pos) and (playlist_user.position <= new_pos):
                    await UsersPlaylistsDAO.update(playlist_user, {'position': playlist_user.position - 1})

    except Exception as e:
        print(f"/updatePlaylistsPosition Exception: {str(e)}")
        raise
    
    user_playlist = await UsersPlaylistsDAO.update(db_playlist_user, {'position': new_pos})
    return JSONResponse(
        status_code=200,
        content={
            'message': 'UserPlaylist position updated successfully',
            'playlist_id': user_playlist.playlist_id,
            'user_id': user_playlist.user_id,
            'position': new_pos
        }
    )


@router.delete("/deleteUserPlaylist")
async def delete_user_playlist(playlist_id: int, current_user: User = Depends(get_current_user)):
    """ Эндпоинт для удаления плейлиста пользователя """
    
    up_filter = {
        'playlist_id': playlist_id,
        'user_id': current_user.id
    }

    user_playlist = await UsersPlaylistsDAO.find_one_or_none(**up_filter)
    if not user_playlist:
        raise NoUserPlaylistException
    
    playlist = await PlaylistsDAO.find_one_or_none_by_id(playlist_id)
    is_author = playlist.author_id == current_user.id
    if is_author:
        playlist = await PlaylistsDAO.delete(playlist_id)

    await UsersPlaylistsDAO.delete(user_playlist.id)
    return {"message": "Deleted successfully"}