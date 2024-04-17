from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, VARCHAR

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(VARCHAR, nullable=False)
    password = Column(VARCHAR, nullable=False)
    name = Column(VARCHAR, nullable=True)
    surname = Column(VARCHAR, nullable=True)
    phone = Column(VARCHAR, nullable=True)
    email = Column(VARCHAR, nullable=True)
    birthdate = Column(TIMESTAMP, nullable=True)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    users_id = Column(Integer, ForeignKey('users.id'))
    title = Column(VARCHAR, nullable=False)
    text = Column(VARCHAR, nullable=False)
    creation_date = Column(TIMESTAMP, nullable=False)
