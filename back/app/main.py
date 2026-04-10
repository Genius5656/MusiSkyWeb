from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.exceptions import TokenExpiredException, TokenNoFoundException
from app.users.router import router as users_router
from app.tracks.router import router as tracks_router
from app.playlists.router import router as playlists_router
from app.tracks_playlists.router import router as tracks_playlists_router
from app.users_playlists.router import router as users_playlists_router
from app.youtube.router import router as youtube_router
from app.users_tracks.router import router as users_tracks_router
from app.media_interaction import BASE_DIR, MEDIA_TRACKS_MP3, MEDIA_TRACKS_IMAGES, MEDIA_COVER_IMAGES
import uvicorn

app = FastAPI(title="Music Player API", description="Веб плеер")

""" app.mount('/static', StaticFiles(directory='app/static'), name='static') """
app.mount("/media/tracks_mp3", StaticFiles(directory=str(MEDIA_TRACKS_MP3)), name="tracks_mp3")
app.mount("/media/tracks_images", StaticFiles(directory=str(MEDIA_TRACKS_IMAGES)), name="tracks_images")
app.mount("/media/cover_images", StaticFiles(directory=str(MEDIA_COVER_IMAGES)), name="cover_images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любых источников. Можете ограничить список доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

app.include_router(users_router)
app.include_router(tracks_router)
app.include_router(playlists_router)
app.include_router(tracks_playlists_router)
app.include_router(users_playlists_router)
app.include_router(users_tracks_router)
app.include_router(youtube_router)


""" @app.get("/")
async def redirect_to_auth():
    return RedirectResponse(url="/auth")


@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(request: Request, exc: HTTPException):
    # Возвращаем редирект на страницу /auth
    return RedirectResponse(url="/auth")


# Обработчик для TokenNoFound
@app.exception_handler(TokenNoFoundException)
async def token_no_found_exception_handler(request: Request, exc: HTTPException):
    # Возвращаем редирект на страницу /auth
    return RedirectResponse(url="/auth") """


# --- Точка входа для тестирования ---
if __name__ == "__main__":
    # Запустите сервер командой: uvicorn main:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8001)
