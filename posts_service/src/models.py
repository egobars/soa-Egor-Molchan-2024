from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, VARCHAR

from db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    users_id = Column(Integer, nullable=False)
    author = Column(VARCHAR, nullable=False)
    title = Column(VARCHAR, nullable=False)
    text = Column(VARCHAR, nullable=False)
    creation_date = Column(TIMESTAMP, nullable=False)
