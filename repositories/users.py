from sqlalchemy import select

from database import new_session
from models.clients_orm import ClientsOrm
from models.managers_orm import ManagersOrm


class UsersRepository:
    @classmethod
    async def get_all_managers(cls) -> list[ManagersOrm]:
        async with new_session() as session:
            query = select(ManagersOrm)
            result = await session.execute(query)
            manager_models = result.scalars().all()
            managers = [manager_model for manager_model in manager_models]
            return managers

    @classmethod
    async def add_client(cls, client: ClientsOrm) -> int:
        async with new_session() as session:
            new_client = client
            session.add(client)
            await session.flush()
            await session.commit()
            return new_client.client_id
