from sqlalchemy import ForeignKey, Column, Integer, String, Float, BIGINT
from sqlalchemy.orm import relationship

from database import Base


class ClaimsOrm(Base):
    __tablename__ = 'claims'

    claim_id = Column(Integer, primary_key=True)
    client_id = Column(BIGINT, ForeignKey('clients.telegram_id'), unique=True)
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'), unique=True)
    email = Column(String)
    description = Column(String)
    amount = Column(Float)
    docs = Column(String)

    # Определяем отношение с таблицей клиентов
    client = relationship("ClientsOrm", back_populates="claims")
    # Определяем отношение с таблицей накладных
    invoices = relationship("InvoicesOrm", back_populates="claims")

