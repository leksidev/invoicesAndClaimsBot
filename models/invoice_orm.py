from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base


class InvoicesOrm(Base):
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