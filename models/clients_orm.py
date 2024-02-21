from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base


class ClientsOrm(Base):
    __tablename__ = 'clients'
    client_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey('managers.manager_id'))
    manager = relationship("ManagerOrm", back_populates="clients")