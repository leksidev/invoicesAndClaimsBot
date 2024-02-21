from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class ClaimsOrm(Base):
    __tablename__ = 'claims'
    claim_id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.client_id'), unique=True)
    invoice_id: Mapped[int]
    email: Mapped[str]
    description: Mapped[str]
    refund_amount: Mapped[float]
    added_docs: Mapped[str]
    clients = relationship("ClientsOrm", back_populates="claims")