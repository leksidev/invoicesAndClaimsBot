import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from database import create_tables, delete_tables
from utils.commands import set_commands

from handlers import main_menu, create_invoice, create_claim

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


async def start_bot(bot: Bot) -> None:
    await create_tables()
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

    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(create_invoice.router, create_claim.router, main_menu.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
