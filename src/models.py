from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class CreateUser(BaseUser):
    name: str = Field(min_length=2, max_length=100)


class UpdateUser(CreateUser):
    pass


class PublicUser(BaseModel):
    id: int
    email: EmailStr
    name: str
