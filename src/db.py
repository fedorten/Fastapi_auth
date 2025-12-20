from sqlmodel import SQLModel, create_engine, Field, Session, select
from fastapi import HTTPException, Depends
from typing import Annotated
from sqlalchemy.exc import IntegrityError

from src.models import CreateUser, UpdateUser
from src.secure import get_password_hash

db_url = "sqlite:///my_db.db"
engine = create_engine(db_url, connect_args={"check_same_thread": False})


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    email: str = Field(unique=True)
    password: str = Field(min_length=6, max_length=100)  # cash_password


def create_database_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def delete_user(user_id, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    session.delete(user)
    session.commit()
    return f"user {user_id} was deleted"


def update_user(user_id, updating_user: UpdateUser, session: SessionDep):
    user = session.get(User, user_id)
    new_user = User(**updating_user.model_dump())
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    user.name, user.email, user.password = (
        new_user.name,
        new_user.email,
        get_password_hash(new_user.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def creating_user(user_data: CreateUser, session: SessionDep):
    try:
        user = User(**user_data.model_dump())
        user.password = get_password_hash(user_data.password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="this Email already using")


def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users


def get_user_by_id(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user
