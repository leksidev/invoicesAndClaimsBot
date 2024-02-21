import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from db.connect import create_tables
from utils.commands import set_commands

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


async def start_bot(bot: Bot) -> None:
    await set_commands(bot)
    await create_tables()
    await bot.send_message(os.environ["ADMIN_ID"], text="Бот запущен!")


async def stop_bot(bot: Bot):
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

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
