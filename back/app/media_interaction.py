import uuid
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, error
from app.exceptions import FilesNotAllowedException
from fastapi import HTTPException
from PIL import Image
import io
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_TRACKS_MP3 = BASE_DIR / "media" / "tracks_mp3"
MEDIA_TRACKS_IMAGES = BASE_DIR / "media" / "tracks_images"
MEDIA_COVER_IMAGES = BASE_DIR / "media" / "cover_images"

# Создаем директории если их нет
MEDIA_TRACKS_MP3.mkdir(parents=True, exist_ok=True)
MEDIA_TRACKS_IMAGES.mkdir(parents=True, exist_ok=True)
MEDIA_COVER_IMAGES.mkdir(parents=True, exist_ok=True)


def extract_metadata_from_mp3(file_path: Path) -> dict:
    """Извлечение метаданных из MP3 файла"""
    metadata = {
        'title': None,
        'artist': None,
        'album': None,
        'image_data': None
    }
    
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # Проверяем наличие ID3 тегов
        if audio.tags:
            # Извлекаем название трека
            if 'TIT2' in audio.tags:
                metadata['title'] = str(audio.tags['TIT2'])
            
            # Извлекаем исполнителя
            if 'TPE1' in audio.tags:
                metadata['artist'] = str(audio.tags['TPE1'])
            
            # Извлекаем альбом
            if 'TALB' in audio.tags:
                metadata['album'] = str(audio.tags['TALB'])
            
            # Извлекаем обложку
            if 'APIC:' in audio.tags:
                apic = audio.tags['APIC:']
                metadata['image_data'] = apic.data
            elif 'APIC' in audio.tags:
                apic = audio.tags['APIC']
                metadata['image_data'] = apic.data
                
    except Exception as e:
        print(f"Error reading metadata: {e}")
    
    return metadata


def remove_metadata_from_mp3(file_path: Path) -> None:
    """Удаление всех метаданных из MP3 файла"""
    try:
        # Загружаем файл с ID3 тегами
        audio = ID3(file_path)
        
        # Удаляем все теги
        audio.delete()
        audio.save()
        
        print(f"Metadata removed from {file_path}")
    except error:
        # Если файл не содержит ID3 тегов
        print(f"No ID3 tags found in {file_path}")
    except Exception as e:
        print(f"Error removing metadata: {e}")


def save_image(image_data: bytes, dir: str) -> str:
    """Сохранение изображения в файловую систему"""
    if not image_data:
        return None
    
    # Генерируем уникальное имя файла
    filename = f"{uuid.uuid4().hex}.jpg"
    if dir == "tracks":
        file_path = MEDIA_TRACKS_IMAGES / filename
    elif dir == "playlists":
        file_path = MEDIA_COVER_IMAGES / filename
    
    try:
        # Конвертируем и сохраняем изображение
        image = Image.open(io.BytesIO(image_data))
        
        # Конвертируем в RGB если необходимо
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        image.save(file_path, 'JPEG', quality=95)
        return f"/media/tracks_images/{filename}"
    
    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def convert_image_to_bytes(image_file) -> bytes:
    """Конвертирует загруженное изображение в байты"""
    try:
        # Читаем содержимое файла
        contents = image_file.file.read()
        
        # Открываем изображение с помощью PIL для валидации
        image = Image.open(io.BytesIO(contents))
        
        # Конвертируем в RGB если необходимо (для JPEG)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Сохраняем в байты
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=95)
        
        return img_byte_arr.getvalue()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


def delete_file_by_path(file_path: str) -> bool:
    """
    Удаляет файл по указанному пути
    
    Args:
        file_path (str): Путь к файлу (абсолютный или относительный)
        
    Returns:
        bool: True если файл успешно удален, False если файл не существует
        
    Raises:
        HTTPException: При ошибках доступа или других проблемах
    """
    try:
        # Преобразуем строку в Path объект
        path = Path(file_path)
        
        # Проверяем существует ли файл
        if not path.exists():
            return False
        
        # Проверяем является ли это файлом (не директорией)
        if not path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {file_path}")
        
        # Проверяем права на удаление
        if not os.access(path.parent, os.W_OK):
            raise HTTPException(status_code=403, detail=f"No write permission for directory: {path.parent}")
        
        # Удаляем файл
        path.unlink()
        
        return True
        
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied: {file_path}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"OS error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")