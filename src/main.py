from fastapi import FastAPI
from contextlib import asynccontextmanager

from src import users
from src.db import create_database_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)
