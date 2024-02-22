from sqlalchemy import select

from database import new_session
from models.invoice_orm import InvoicesOrm


class InvoiceRepository:
    @classmethod
    async def add_invoice(cls, invoice: InvoicesOrm) -> int:
        async with (new_session() as session):
            invoice.weight = float(invoice.weight)
            invoice.height = float(invoice.height)
            invoice.width = float(invoice.width)
            invoice.length = float(invoice.length)
            new_invoice = invoice
            session.add(invoice)
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

    @classmethod
    async def get_all_user_invoices(cls, client_id: int) -> list[int]:
        async with new_session() as session:
            query = select(InvoicesOrm).where(InvoicesOrm.client_id == client_id)
            result = await session.execute(query)
            invoice_models = result.scalars().all()
            invoices = [invoice_model.invoice_id for invoice_model in invoice_models]
            return invoices

