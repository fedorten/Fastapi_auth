from fastapi import APIRouter, HTTPException, Depends

from src.db import (
    get_users,
    get_user_by_id,
    creating_user,
    delete_user,
    update_user,
    SessionDep,
)
from src.models import CreateUser, UpdateUser, PublicUser
from src.secure import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/", response_model=list[PublicUser])
async def read_users(session: SessionDep):
    return get_users(session)


@router.get("/{id}", response_model=PublicUser)
async def read_user(id: int, session: SessionDep):
    user = get_user_by_id(id, session)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@router.post("/", response_model=PublicUser)
async def create_user(user: CreateUser, session: SessionDep):
    user = creating_user(user, session)
    if not user:
        raise HTTPException(status_code=409, detail="this Email already using")
    return user


@router.delete("/{id}", response_model=PublicUser)
async def remove_user(id: int, session: SessionDep):
    user = delete_user(id, session)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@router.put("/{id}", response_model=PublicUser)
async def transform_user(
    id: int,
    user: UpdateUser,
    session: SessionDep,
    current_user=Depends(get_current_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profile",
        )
    user = update_user(id, user, session)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user
