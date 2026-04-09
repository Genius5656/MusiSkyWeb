from fastapi import status, HTTPException


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек")


class TokenNoFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не найден")


UserAlreadyExistsException = HTTPException(status_code=status.HTTP_409_CONFLICT,
                                           detail='Пользователь уже существует')

PasswordMismatchException = HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Пароли не совпадают!')

IncorrectEmailOrPasswordException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                  detail='Неверная почта или пароль')

NoJwtException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                               detail='Токен не валидный!')

NoUserIdException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                  detail='Не найден ID пользователя')

ForbiddenException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав!')

NoUserException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

UserAlreadyBannedException = HTTPException(status_code=status.HTTP_409_CONFLICT,
                                           detail='Пользователь уже забанен')

NoBannedUserException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не находится в банлисте")

UserInBanException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь находится в банлисте")



TrackAlreadyExistsException = HTTPException(status_code=status.HTTP_409_CONFLICT,
                                           detail='Трек уже существует')

NoTrackException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")

FilesNotAllowedException = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Данный тип файла не поддерживается!")

NoPlaylistException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")



NoTrackPlaylistException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TrackPlaylist not found")

NoUserPlaylistException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UserPlaylist not found")