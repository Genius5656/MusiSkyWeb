from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class TracksCreate(BaseModel):
    file: UploadFile = File(...)
    #privacy: bool 


class TracksRead(BaseModel):
    id: int
    yt_id: Optional[str]
    track_url: Optional[str]
    img_url: Optional[str]
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]

    class Config:
        from_attributes = True


class TracksUpdate(BaseModel):
    views_all: int
    views_date: int