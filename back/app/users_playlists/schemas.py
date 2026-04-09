from typing import Optional
from pydantic import BaseModel, Field


class UsersPlaylistsCreate(BaseModel):
    user_id: int
    playlist_id: int
    position: int


class UsersPlaylistsRead(BaseModel):
    id: int
    user_id: int
    playlist_id: int
    position: int

    class Config:
        from_attributes = True


class UsersPlaylistsUpdate(BaseModel):
    playlist_id: int
    user_id: int
    position: int


class UsersPlaylistsDelete(BaseModel):
    playlist_id: int
    user_id: int
    