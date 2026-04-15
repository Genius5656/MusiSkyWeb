from pathlib import Path
from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.responses import JSONResponse
from app.media_interaction import save_image, convert_image_to_bytes, delete_file_by_path
from app.exceptions import NoPlaylistException, FilesNotAllowedException
from app.users.dependensies import get_current_user
from app import User
from app.playlists.dao import PlaylistsDAO
from app.tracks.dao import TracksDAO
from app.tracks_playlists.dao import TracksPlaylistsDAO
from app.playlists.schemas import PlaylistsCreate, PlaylistsRead, PlaylistsUpdate
import urllib.parse

router = APIRouter(prefix='/playlists', tags=['Playlists'])


@router.get("/playlists/{playlist_id}", response_model=PlaylistsRead)
async def get_playlist_by_id(playlist_id: int, current_user: User = Depends(get_current_user)):
    """ Получение информации о плейлисте """
    playlist = await PlaylistsDAO.find_one_or_none(id=playlist_id)
    if not playlist:
        raise NoPlaylistException
    
    can_edit = current_user.id == playlist.author_id
    
    return PlaylistsRead(
        id = playlist.id,
        yt_id = playlist.yt_id,
        author_id = playlist.author_id,
        title = playlist.title,
        img_url = playlist.img_url,
        privacy = playlist.privacy,
        can_edit = can_edit
    )


@router.post("/addPlaylist")
async def add_playlist(playlist: PlaylistsCreate, author: User = Depends(get_current_user)):
    """Эндпоинт для загрузки картинки плейлиста"""
    
    # Проверяем допустимые расширения
    if playlist.file != None:
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.svg'}
        file_extension = Path(playlist.file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise FilesNotAllowedException
    
    try:
        img_url = None

        if playlist.file != None:
            # Конвертируем изображение в байты
            image_bytes = convert_image_to_bytes(playlist.file)
            
            # Сохраняем изображение используя существующую функцию save_image
            img_url = save_image(image_bytes, "playlists")
            
            if not img_url:
                raise HTTPException(status_code=500, detail="Failed to save image")
            
            img_url = urllib.parse.quote(img_url)
        
        # Сохраняем данные в БД
        playlist_data = {
            'yt_id': None,
            'author_id': author.id,
            'title': playlist.title,
            'img_url': img_url,
            'privacy': playlist.privacy
        }
        
        new_playlist = await PlaylistsDAO.add(**playlist_data)
        
        return JSONResponse(
            status_code=200,
            content={
                'message': 'Playlist added successfully',
                'playlist_id': new_playlist.id,
                'img_url': img_url,
                'author_id': author.id,
                'metadata': {
                    'title': playlist.title
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing add image: {str(e)}")


@router.put("/updatePlaylist/{playlist_id}", response_model=PlaylistsRead)
async def update_playlist(playlist_id: int, playlist: PlaylistsUpdate):
    """Эндпоинт для изменения плейлиста"""

    db_playlist = await PlaylistsDAO.find_one_or_none(id=playlist_id)
    if not db_playlist:
        raise NoPlaylistException
    
    try:
        if db_playlist.img_url:
            cover_path = urllib.parse.unquote(playlist.img_url)
            delete_file_by_path(cover_path)

        img_url = None

        if playlist.file:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.svg'}
            file_extension = Path(playlist.file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                raise FilesNotAllowedException
            
            # Конвертируем изображение в байты
            image_bytes = convert_image_to_bytes(playlist.file)
            
            # Сохраняем изображение используя существующую функцию save_image
            img_url = save_image(image_bytes, "playlists")
            
            if not img_url:
                raise HTTPException(status_code=500, detail="Failed to save image")
            
            img_url = urllib.parse.quote(img_url)

        playlist_data = {
            'title': playlist.title,
            'img_url': img_url,
            'privacy': playlist.privacy
        }

        playlistUpdate = await PlaylistsDAO.update(db_playlist, playlist_data)

        return JSONResponse(
            status_code=200,
            content={
                'message': 'Playlist updated successfully',
                'playlist_id': playlistUpdate.id,
                'img_url': img_url,
                'author_id': playlistUpdate.author_id,
                'metadata': {
                    'title': playlist.title,
                    'privacy': playlist.privacy
                }
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing update: {str(e)}")


@router.delete("/deletePlaylist/{playlist_id}")
async def delete_playlist(playlist_id: int):
    """Эндпоинт для удаления плейлиста"""


    playlist = await PlaylistsDAO.find_one_or_none_by_id(playlist_id)
    if not playlist:
        raise NoPlaylistException
    
    cover_path = None
    try:
        cover_path = urllib.parse.unquote(playlist.img_url)
    except:
        print("Ошибка при обработке пути обложки")
    cover_del = delete_file_by_path(cover_path)
    if not cover_del:
        print("Обложка отсутствует")
    
    await PlaylistsDAO.delete(playlist_id)
        
    return {"message": "Deleted successfully"}