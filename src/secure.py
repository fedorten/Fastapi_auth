from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from datetime import timezone, datetime, timedelta

from src.db import SessionDep, get_user_by_email, get_user_by_id

router = APIRouter(tags=["secure"])

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

tokenDep = Annotated[str, Depends(oauth_scheme)]


SECRET_KEY = "fe31eee4a2f653b9b467224786cc4bf56fb4db6cb26ee1cd11e06a92814f43c7"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = (60 * 24) * 14

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

password_hash = PasswordHash.recommended()


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """создание jwt токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    """возвращает закешированный пароль"""
    return password_hash.hash(password)


def verify_password(password, hashed_password):
    """сравнивает пароль и закешированный пороль в бд"""
    return password_hash.verify(password, hashed_password)


def authenticate_user(session: SessionDep, username: str, password: str):
    """аунтефицирует юзера по почте и поролю"""
    user = get_user_by_email(username, session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)], session: SessionDep
):
    """получает юзера только если у него есть jwt и он корректный"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise CREDENTIALS_EXCEPTION
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            raise CREDENTIALS_EXCEPTION

    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION

    user = get_user_by_id(user_id_int, session)
    if user is None:
        raise CREDENTIALS_EXCEPTION

    return user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    """создание токена на основе формы(например из SWAGGER)"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
