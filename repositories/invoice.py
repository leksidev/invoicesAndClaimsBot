from sqlalchemy import select

from database import new_session
from models.invoice_orm import InvoicesOrm


class InvoiceRepository:
    @classmethod
    async def add_invoice(cls, invoice: InvoicesOrm) -> int:
        async with new_session() as session:
            data = invoice.model_dump()
            new_invoice = InvoicesOrm(**data)
            session.add(new_invoice)
            await session.flush()
            await session.commit()
            return new_invoice.invoice_id

    @classmethod
    async def get_invoice(cls, invoice_id: int) -> InvoicesOrm:
        async with new_session() as session:
            query = select(InvoicesOrm).where(InvoicesOrm.invoice_id == invoice_id)
            result = await session.execute(query)
            invoice_model = result.scalar()
            invoice = invoice_model
            return invoice

    @classmethod
    async def get_all_invoices(cls) -> list[InvoicesOrm]:
        async with new_session() as session:
            query = select(InvoicesOrm)
            result = await session.execute(query)
            invoice_models = result.scalars().all()
            invoices = [invoice_model for invoice_model in invoice_models]
            return invoices
