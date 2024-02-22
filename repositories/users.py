from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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
            # Проверяем наличие telegram_id в базе данных
            stmt = select(ClientsOrm).filter_by(telegram_id=client.telegram_id)
            existing_client = await session.execute(stmt)
            existing_client = existing_client.scalar_one_or_none()
            if existing_client:
                # Клиент с таким telegram_id уже существует
                raise ValueError("Client with this telegram_id already exists")

            # Добавляем клиента в базу данных
            session.add(client)
            try:
                await session.flush()
                await session.commit()
                return client.client_id
            except IntegrityError:
                # Обработка случая, когда возникает ошибка IntegrityError
                await session.rollback()
                raise ValueError("Failed to add client due to integrity constraint violation")

    from sqlalchemy.exc import IntegrityError

    @classmethod
    async def add_manager(cls, manager: ManagersOrm) -> int:
        async with new_session() as session:
            # Проверяем наличие telegram_id в базе данных
            stmt = select(ClientsOrm).filter_by(telegram_id=manager.telegram_id)
            existing_manager = await session.execute(stmt)
            existing_manager = existing_manager.scalar_one_or_none()
            if existing_manager:
                # Менеджер с таким telegram_id уже существует
                raise ValueError("Manager with this telegram_id already exists")

            # Добавляем менеджера в базу данных
            session.add(manager)
            try:
                await session.flush()
                await session.commit()
                return manager.manager_id
            except IntegrityError:
                # Обработка случая, когда возникает ошибка IntegrityError
                await session.rollback()
                raise ValueError("Failed to add manager due to integrity constraint violation")
