from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends
from pwdlib import PasswordHash


auth_scheme = OAuth2PasswordBearer(tokenUrl="token")

tokenDep = Annotated[str, Depends(auth_scheme)]


SECRET_KEY = "fe31eee4a2f653b9b467224786cc4bf56fb4db6cb26ee1cd11e06a92814f43c7"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTS = (60 * 24) * 14

password_hash = PasswordHash.recommended()


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(password, hashed_passwor):
    return password_hash.verify(password, hashed_passwor)
