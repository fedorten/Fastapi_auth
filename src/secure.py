from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from datetime import timezone, datetime, timedelta

from src.db import SessionDep, get_user_by_email, get_user_by_id


oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

tokenDep = Annotated[str, Depends(oauth_scheme)]


SECRET_KEY = "fe31eee4a2f653b9b467224786cc4bf56fb4db6cb26ee1cd11e06a92814f43c7"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = (60 * 24) * 14

password_hash = PasswordHash.recommended()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)


def authenticate_user(session: SessionDep, username: str, password: str):
    user = get_user_by_email(email=username, session=session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)], session: SessionDep
):
    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exeption
        token_data = TokenData(user_id=user_id)

    except jwt.PyJWTError:
        raise credentials_exeption

    user = get_user_by_id(token_data.user_id, session=session)
    if user is None:
        raise credentials_exeption

    return user
