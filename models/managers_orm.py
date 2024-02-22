from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ManagersOrm(Base):
    __tablename__ = 'managers'
    manager_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
