import logging
import os

from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from database import create_tables, delete_tables
from models.model import Manager
from services import add_manager
from utils.commands import set_commands

from handlers import main_menu, create_invoice, create_claim, get_climes_list

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


async def start_bot(bot: Bot) -> None:
    await create_tables()
    await add_manager(Manager(telegram_id=int(os.environ["ADMIN_ID"]), chat_id=int(os.environ["ADMIN_ID"])))
    await set_commands(bot)
    await bot.send_message(os.environ["ADMIN_ID"], text="Бот запущен!")


async def stop_bot(bot: Bot):
    await delete_tables()
    await bot.send_message(os.environ["ADMIN_ID"], text="Бот остановлен!")


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    )
    bot = Bot(token=os.environ["BOT_TOKEN"])

    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(main_menu.router,
                       create_invoice.router,
                       create_claim.router,
                       get_climes_list.router,
                       )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
