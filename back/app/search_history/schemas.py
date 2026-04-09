from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class TracksCreate(BaseModel):
    file: UploadFile = File(...)
    #privacy: bool 


class TracksRead(BaseModel):
    id: int
    yt_id: str
    track_url: str
    image_url: str
    title: str
    artist: str
    album: str
    views_all: int
    views_date: int
    privacy: int

    class Config:
        from_attributes = True


class TracksUpdate(BaseModel):
    views_all: int
    views_date: int