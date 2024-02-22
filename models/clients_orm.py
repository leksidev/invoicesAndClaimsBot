from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ClientsOrm(Base):
    __tablename__ = 'clients'
    client_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    invoices = relationship("InvoicesOrm", back_populates="client")
    claims = relationship("ClaimsOrm", back_populates="client")
