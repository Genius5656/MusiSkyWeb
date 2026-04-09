import uuid
import shutil
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from app.media_interaction import BASE_DIR, MEDIA_TRACKS_MP3, MEDIA_TRACKS_IMAGES, MEDIA_COVER_IMAGES
from app.media_interaction import extract_metadata_from_mp3, remove_metadata_from_mp3, save_image, delete_file_by_path
from app.exceptions import TrackAlreadyExistsException, NoTrackException, FilesNotAllowedException
from app.tracks.dao import TracksDAO
from app.tracks.schemas import TracksCreate, TracksRead, TracksUpdate
import urllib.parse

router = APIRouter(prefix='/tracks', tags=['Tracks'])


@router.get("/tracks/{track_id}", response_model=TracksRead)
async def get_track_by_id(track_id: int):
    """Получение информации о треке"""
    track = await TracksDAO.find_one_or_none_by_id(track_id)
    if not track:
        raise NoTrackException
    
    return {
        'id': track.id,
        'track_url': track.track_url,
        'img_url': track.img_url,
        'title': track.title,
        'artist': track.artist,
        'album': track.album,
        'views_all': track.views_all,
        'views_date': track.views_date,
        'privacy': track.privacy
    }


@router.post("/addLocalTrack")
async def add_local_track(track: TracksCreate):
    """Эндпоинт для загрузки и обработки MP3 файла"""
    
    # Проверяем тип файла
    if not track.file.filename.endswith('.mp3'):
        raise FilesNotAllowedException
    
    # Сохраняем временный файл
    temp_file_path = BASE_DIR / "media" / "temp" / f"temp_{uuid.uuid4().hex}.mp3"
    temp_file_path.parent.mkdir(exist_ok=True)
    
    try:
        # Сохраняем загруженный файл
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(track.file.file, buffer)
        
        # Извлекаем метаданные
        metadata = extract_metadata_from_mp3(temp_file_path)

        """ exist_track = await TracksDAO.find_one_or_none(metadata['title'])
        if exist_track:
            raise TrackAlreadyExistsException """
        
        # Сохраняем изображение если есть
        img_url = None
        if metadata['image_data']:
            img_url = save_image(metadata['image_data'], "tracks")
            img_url = urllib.parse.quote(img_url)
        
        # Генерируем уникальное имя для очищенного MP3
        mp3_filename = f"{uuid.uuid4().hex}.mp3"
        mp3_file_path = MEDIA_TRACKS_MP3 / mp3_filename
        
        # Копируем временный файл в конечную директорию
        shutil.copy2(temp_file_path, mp3_file_path)
        
        # Удаляем метаданные из скопированного файла
        remove_metadata_from_mp3(mp3_file_path)
        
        # Формируем URL для доступа к файлам
        track_url = f"/media/tracks_mp3/{mp3_filename}"
        track_url = urllib.parse.quote(track_url)
        
        # Сохраняем информацию в БД
        track_data = {
            'yt_id': "",
            'track_url': track_url,
            'img_url': img_url or "",
            'title': metadata['title'],
            'artist': metadata['artist'],
            'album': metadata['album'],
            'views_all': 0,
            'views_date': 0,
            #'privacy': track.privacy
        }
        
        new_track = await TracksDAO.add(**track_data)
        
        return JSONResponse(
            status_code=200,
            content={
                'message': 'File uploaded and processed successfully',
                'track_id': new_track.id,
                'track_url': track_url,
                'img_url': img_url,
                'metadata': {
                    'title': metadata['title'],
                    'artist': metadata['artist'],
                    'album': metadata['album']
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if temp_file_path.exists():
            temp_file_path.unlink()


@router.put("/updateTrackViews/{track_id}", response_model=TracksRead)
async def update_track(track_id: int, track: TracksUpdate):
    """Эндпоинт для изменения просмотров трека"""

    db_track = await TracksDAO.find_one_or_none_by_id(track_id)
    if not db_track:
        raise NoTrackException

    track = TracksUpdate(views_all=track.views_all, views_date=track.views_date)
    trackUpdate = await TracksDAO.update(db_track, track)
    return trackUpdate


@router.delete("/deleteTrack/{track_id}", response_model=TracksRead)
async def delete_track(track_id: int):
    """Эндпоинт для удаления трека"""

    track = await TracksDAO.find_one_or_none_by_id(track_id)
    if not track:
        raise NoTrackException
    
    track_path = urllib.parse.unquote(track.track_url)
    track_del = delete_file_by_path(track_path)
    if not track_del:
        print("Трек mp3 отсутствует")

    cover_path = urllib.parse.unquote(track.img_url)
    cover_del = delete_file_by_path(cover_path)
    if not cover_del:
        print("Обложка отсутствует")

    track = await TracksDAO.delete(id=track_id)
    return track