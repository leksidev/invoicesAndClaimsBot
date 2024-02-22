from sqlalchemy import ForeignKey, Column, Integer, String, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base


class ClaimsOrm(Base):
    __tablename__ = 'claims'

    claim_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.client_id'), unique=True)
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'), unique=True)
    email = Column(String)
    description = Column(String)
    amount = Column(Float)
    docs = Column(String)

    # Определяем отношение с таблицей клиентов
    client = relationship("ClientsOrm", back_populates="claims")
    # Определяем отношение с таблицей счетов
    invoices = relationship("InvoicesOrm", back_populates="claims")

