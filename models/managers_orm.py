from sqlalchemy import Column, Integer, BIGINT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ManagersOrm(Base):
    __tablename__ = 'managers'
    manager_id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True)
    chat_id = Column(BIGINT, unique=True)