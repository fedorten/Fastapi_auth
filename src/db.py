from sqlmodel import SQLModel, create_engine, Field, Session, select
from fastapi import Depends
from typing import Annotated
from sqlalchemy.exc import IntegrityError

from src.models import CreateUser, UpdateUser


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


def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        return None
    session.delete(user)
    session.commit()
    return user


def update_user(user_id: int, updating_user: UpdateUser, session: SessionDep):
    from src.secure import get_password_hash

    try:
        user = session.get(User, user_id)
        new_user = User(**updating_user.model_dump())
        if not user:
            return None

        user.name, user.email, user.password = (
            new_user.name,
            new_user.email,
            get_password_hash(new_user.password),
        )

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        return None


def creating_user(user_data: CreateUser, session: SessionDep):
    from src.secure import get_password_hash

    try:
        user = User(**user_data.model_dump())
        user.password = get_password_hash(user_data.password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        return None


def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users


def get_user_by_id(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        return None
    return user


def get_user_by_email(email: str, session: SessionDep):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    return user
