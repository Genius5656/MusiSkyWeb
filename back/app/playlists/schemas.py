from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class PlaylistsCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    file: Optional[UploadFile] = None
    privacy: bool


class PlaylistsRead(BaseModel):
    id: int
    yt_id: Optional[str]
    author_id: int
    title: str
    img_url: Optional[str]
    privacy: bool
    can_edit: bool

    class Config:
        from_attributes = True


class PlaylistsUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    file: Optional[UploadFile] = None
    privacy: bool