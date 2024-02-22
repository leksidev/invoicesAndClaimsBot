import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

engine = create_async_engine(f"postgresql+asyncpg://{os.environ['POSTGRES_USER']}:"
                             f"{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:"
                             f"{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}",
                             echo=False)
new_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
