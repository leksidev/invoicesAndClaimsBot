import os

from aiogram import Bot
from dotenv import load_dotenv
from sqlalchemy import select

from database import new_session
from models.model import Claim, Invoice, Client, Manager, ChatRequest

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = Bot(token=os.environ["BOT_TOKEN"])


async def get_opened_chats() -> list[ChatRequest]:
    async with new_session() as session:
        query = select(ChatRequest).where(ChatRequest.is_opened == True)
        result = await session.execute(query)
        return result.scalars().all()


async def send_chat_request(chat_request: ChatRequest):
    async with new_session() as session:
        query = select(ChatRequest).where(ChatRequest.client_id == chat_request.client_id)
        result = await session.execute(query)
        existing_chat_request = result.scalar()
        if existing_chat_request:
            existing_chat_request.is_opened = True
        else:
            session.add(chat_request)
        await session.flush()
        await session.commit()


async def close_chat(chat_id: int) -> int:
    async with new_session() as session:
        query = select(ChatRequest).where(ChatRequest.manager_id == chat_id or ChatRequest.client_id == chat_id)
        result = await session.execute(query)
        chat_request = result.scalar()
        chat_request.is_opened = False
        session.add(chat_request)
        await session.flush()
        await session.commit()
        return chat_request


async def check_chat_status(chat_id: int) -> bool:
    async with new_session() as session:
        query = select(ChatRequest).where(ChatRequest.manager_id == chat_id or ChatRequest.client_id == chat_id)
        result = await session.execute(query)
        chat_request = result.scalar()
        return chat_request.is_opened


async def add_client(client: Client) -> int:
    async with new_session() as session:
        query = select(Client).where(Client.client_id == client.client_id)
        result = await session.execute(query)
        if not result.scalar():
            session.add(client)
            await session.flush()
            await session.commit()
            return client.client_id


async def add_manager(manager: Manager) -> int:
    async with new_session() as session:
        query = select(Manager).where(Manager.manager_id == manager.manager_id)
        result = await session.execute(query)
        if not result.scalar():
            session.add(manager)
            await session.flush()
            await session.commit()
            return manager.manager_id


async def add_manager_to_client(client_id: int, manager_id: int) -> int:
    async with new_session() as session:
        query = select(Client).where(Client.client_id == client_id)
        result = await session.execute(query)
        client = result.scalar()
        client.manager_id = manager_id
        session.add(client)
        await session.flush()
        await session.commit()
        return client


async def get_manager_id(client_id: int) -> int:
    async with new_session() as session:
        query = select(Client).where(Client.telegram_id == client_id)
        result = await session.execute(query)
        client = result.scalar()
        return client.manager_id


async def get_all_managers() -> list[Manager]:
    async with new_session() as session:
        query = select(Manager)
        result = await session.execute(query)
        manager_models = result.scalars().all()
        managers = [manager_model for manager_model in manager_models]
        return managers


async def add_claim(claim: Claim) -> int:
    async with new_session() as session:
        new_claim = claim
        session.add(claim)
        await session.flush()
        await session.commit()
        return new_claim.claim_id


async def get_claim(claim_id: int) -> Claim:
    async with new_session() as session:
        query = select(Claim).where(Claim.claim_id == claim_id)
        result = await session.execute(query)
        claim_model = result.scalar()
        claim = claim_model
        return claim


async def get_all_claims() -> list[Claim]:
    async with new_session() as session:
        query = select(Claim)
        result = await session.execute(query)
        claim_models = result.scalars().all()
        claims = [claim_model for claim_model in claim_models]
        return claims


async def add_invoice(invoice: Invoice) -> int:
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


async def get_invoice(invoice_id: int) -> Invoice:
    async with new_session() as session:
        query = select(Invoice).where(Invoice.invoice_id == invoice_id)
        result = await session.execute(query)
        invoice_model = result.scalar()
        invoice = invoice_model
        return invoice


async def get_all_invoices_by_client(client_id: int) -> list[int]:
    async with new_session() as session:
        query = select(Invoice).where(Invoice.client_id == client_id)
        result = await session.execute(query)
        invoice_models = result.scalars().all()
        invoices = [invoice_model.invoice_id for invoice_model in invoice_models]
        return invoices
