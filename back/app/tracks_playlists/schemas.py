from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class TracksPlaylistsCreate(BaseModel):
    file: UploadFile = File(...)
    playlist_id: int
    

class TracksPlaylistsRead(BaseModel):
    id: int
    track_id: int
    playlist_id: int
    position: int

    class Config:
        from_attributes = True


class TracksPlaylistsUpdate(BaseModel):
    track_id: int
    playlist_id: int
    position: int


class TracksPlaylistsDelete(BaseModel):
    track_id: int
    playlist_id: int