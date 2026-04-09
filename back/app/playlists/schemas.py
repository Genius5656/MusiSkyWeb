from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class PlaylistsCreate(BaseModel):
    author_id: int
    title: str = Field(..., min_length=1, max_length=50)
    file: UploadFile | None = None
    privacy: bool


class PlaylistsRead(BaseModel):
    id: int
    yt_id: str
    author_id: int
    title: str
    image_url: str
    privacy: bool
    can_edit: bool

    class Config:
        from_attributes = True


class PlaylistsUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    file: UploadFile | None = None
    privacy: bool