from sqlalchemy import ForeignKey, Column, Integer, String, Float
from sqlalchemy.orm import relationship
from models.clients_orm import ClientsOrm

from database import Base


class InvoicesOrm(Base):
    __tablename__ = 'invoices'

    invoice_id = Column(Integer, primary_key=True)
    description = Column(String)
    weight = Column(Float)
    size = Column(String)
    from_address = Column(String)
    to_address = Column(String)
    pay_method = Column(String)
    telegram_id = Column(Integer, ForeignKey('clients.telegram_id'))
    client = relationship("ClientsOrm", back_populates="invoices")
    claims = relationship("ClaimsOrm", back_populates="invoices")


