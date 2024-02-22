from sqlalchemy import Column, BIGINT, Integer

from database import Base


class ChatOrm(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    manager_id = Column(BIGINT, unique=True)
    client_id = Column(BIGINT, unique=True)
