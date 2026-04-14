from fastapi import APIRouter, Response, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import EmailStr
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, PasswordMismatchException, \
    NoUserException, UserAlreadyBannedException, NoBannedUserException, UserInBanException
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dependensies import get_current_user
from app.users.models import User
from app.users.dao import UsersDAO, BanListDAO
from app.playlists.dao import PlaylistsDAO
from app.users.schemas import SUserRegister, SUserAuth

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(response: Response, user_data: SUserRegister) -> dict:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user:
        raise UserAlreadyExistsException
    
    in_ban = await BanListDAO.find_one_or_none(email=user_data.email)
    if in_ban:
        raise UserInBanException

    if user_data.password != user_data.password_check:
        raise PasswordMismatchException("Пароли не совпадают")
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check == "banned":
        raise UserInBanException
    elif check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)

    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Вы успешно зарегистрированы!'}


@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check == "banned":
        raise UserInBanException
    elif check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.delete("/deleteAccount/")
async def delete_account(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie(key="users_access_token")
    user = await UsersDAO.find_one_or_none_by_id(current_user.id)
    if not user:
        raise NoUserException
    
    playlists = await PlaylistsDAO.find_all(author_id=current_user.id)
    if playlists:
        for playlist in playlists:
            if playlist.author_id == current_user.id:
                await PlaylistsDAO.delete(playlist.id)
    
    user = await UsersDAO.delete(current_user.id)
        
    return {'message': 'Аккаунт удален'}


@router.delete("/deleteUser/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = await UsersDAO.find_one_or_none_by_id(user_id)
    if not user:
        raise NoUserException
    
    playlists = await PlaylistsDAO.find_all(author_id=user_id)
    if playlists:
        for playlist in playlists:
            if playlist.author_id == current_user.id:
                await PlaylistsDAO.delete(playlist.id)

    user = await UsersDAO.delete(user_id)

    return {'message': 'Пользователь удален'}


@router.post("/banUser/{email}")
async def ban_user(response: Response, email: EmailStr):
    banned_user = await BanListDAO.find_one_or_none(email=email)
    if banned_user:
        raise UserAlreadyBannedException

    banned_user = await BanListDAO.add(email=email)
    return {'message': 'Пользователь забанен'}


@router.delete("/unbanUser/{email}")
async def unban_user(email: EmailStr):
    banned_user = await BanListDAO.find_one_or_none(email=email)
    if not banned_user:
        raise NoBannedUserException
    unbanned_user = await BanListDAO.delete(banned_user.id)
    return {'message': 'Пользователь разбанен'}