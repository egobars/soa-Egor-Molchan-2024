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
