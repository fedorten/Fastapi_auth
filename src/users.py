from fastapi import APIRouter

from src.db import (
    get_users,
    get_user_by_id,
    creating_user,
    delete_user,
    update_user,
    SessionDep,
)
from src.models import CreateUser, UpdateUser, PublicUser


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/", response_model=list[PublicUser])
async def read_users(session: SessionDep):
    return get_users(session)


@router.get("/{id}", response_model=PublicUser)
async def read_user(id: int, session: SessionDep):
    return get_user_by_id(id, session)


@router.post("/", response_model=PublicUser)
async def create_user(user: CreateUser, session: SessionDep):
    return creating_user(user, session)


@router.delete("/{id}", response_model=PublicUser)
async def remove_user(id: int, session: SessionDep):
    return delete_user(id, session)


@router.put("/{id}", response_model=PublicUser)
async def transform_user(id: int, user: UpdateUser, session: SessionDep):
    return update_user(id, user, session)
