from sqlalchemy import ForeignKey, Column, Integer, BIGINT
from sqlalchemy.orm import relationship

from database import Base


class ClientsOrm(Base):
    __tablename__ = 'clients'
    client_id = Column(Integer, primary_key=True)
    chat_id = Column(BIGINT, unique=True)
    telegram_id = Column(BIGINT, unique=True)
    invoices = relationship("InvoicesOrm", back_populates="client")
    claims = relationship("ClaimsOrm", back_populates="client")
    manager_id = Column(BIGINT, ForeignKey('managers.telegram_id'))
