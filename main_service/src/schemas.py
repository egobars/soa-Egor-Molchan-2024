import datetime
from pydantic import BaseModel

class AuthSchema(BaseModel):
    login: str
    password: str

class UserCanBeChangedSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    phone: str | None = None
    email: str | None = None
    birthdate: datetime.datetime | None = None

class UserSchema(AuthSchema):
    name: str | None = None
    surname: str | None = None
    phone: str | None = None
    email: str | None = None
    birthdate: datetime.datetime | None = None

    class Config:
        orm_mode = True

class PostWithoutAuthor(BaseModel):
    title: str
    text: str

class Post(PostWithoutAuthor):
    id: int
    author: str
    creationDate: int

    class Config:
        orm_mode = True

class UpdatePost(PostWithoutAuthor):
    post_id: int

    class Config:
        orm_mode = True

class Cursor(BaseModel):
    login: str
    cursor_start: int
    cursor_end: int

class PostStats(BaseModel):
    post_id: int
    likes: int
    views: int

class OnePostStat(BaseModel):
    post_id: int
    author: str
    stat: int

class UserStats(BaseModel):
    login: str
    likes: int
