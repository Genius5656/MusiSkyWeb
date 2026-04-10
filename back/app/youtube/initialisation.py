from ytmusicapi import YTMusic
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    ytmusic = YTMusic()
except Exception as e:
    logger.error(f"Ошибка инициализации YTMusic: {e}")
    ytmusic = None