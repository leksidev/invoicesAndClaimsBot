from sqlalchemy import Column, Integer, BIGINT, BigInteger, Float, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import Base


class ChatRequest(Base):
    __tablename__ = 'chat_requests'
    id = Column(Integer, primary_key=True)
    manager_id = Column(BIGINT)
    client_id = Column(BIGINT)
    is_opened = Column(Boolean, default=True)


class Client(Base):
    __tablename__ = 'clients'
    client_id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    manager_id = Column(BigInteger)
    invoices = relationship("Invoice", back_populates="client")
    claims = relationship("Claim", back_populates="client")


class Manager(Base):
    __tablename__ = 'managers'
    manager_id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    chat_id = Column(BigInteger, unique=True)


class Invoice(Base):
    __tablename__ = 'invoices'

    invoice_id = Column(Integer, primary_key=True)
    description = Column(String)
    weight = Column(Float)
    height = Column(Float)
    width = Column(Float)
    length = Column(Float)
    from_address = Column(String)
    to_address = Column(String)
    pay_method = Column(String)
    client_id = Column(BigInteger, ForeignKey('clients.telegram_id'))
    client = relationship("Client", back_populates="invoices")
    claims = relationship("Claim", back_populates="invoices")


class Claim(Base):
    __tablename__ = 'claims'

    claim_id = Column(Integer, primary_key=True)
    client_id = Column(BigInteger, ForeignKey('clients.telegram_id'))
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'))
    email = Column(String)
    description = Column(String)
    amount = Column(Float)
    docs = Column(String)

    # Определяем отношение с таблицей клиентов
    client = relationship("Client", back_populates="claims")
    # Определяем отношение с таблицей накладных
    invoices = relationship("Invoice", back_populates="claims")
