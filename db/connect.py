import os

from dotenv import load_dotenv
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

engine = create_async_engine(f"postgresql+asyncpg://{os.environ['POSTGRES_USER']}:"
                             f"{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:"
                             f"{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}",
                             echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class InvoicesOrm(Model):
    __tablename__ = 'invoices'
    invoice_id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.client_id'), unique=True)
    description: Mapped[str]
    weight: Mapped[float]
    size: Mapped[str]
    from_address: Mapped[str]
    to_address: Mapped[str]
    pay_method: Mapped[str]
    clients = relationship("ClientsOrm", back_populates="claims")


class ClaimsOrm(Model):
    __tablename__ = 'claims'
    claim_id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.client_id'), unique=True)
    invoice_id: Mapped[int]
    email: Mapped[str]
    description: Mapped[str]
    refund_amount: Mapped[float]
    added_docs: Mapped[str]
    clients = relationship("ClientsOrm", back_populates="claims")


class ClientsOrm(Model):
    __tablename__ = 'clients'
    client_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey('managers.manager_id'))
    manager = relationship("ManagerOrm", back_populates="clients")


class ManagersOrm(Model):
    __tablename__ = 'managers'
    manager_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
    clients = relationship("ClientOrm", back_populates="manager")


async def create_tables():
    """
    Create data tables using the metadata defined in the Model class.
    """
    # Establish a connection to the data engine
    async with engine.begin() as conn:
        # Use the connection to create all tables defined in the metadata
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    """
    Asynchronous function to delete tables using the engine connection.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
