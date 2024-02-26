
from typing import Any, Callable, Dict, Awaitable

from aiogram import Bot, BaseMiddleware, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, TelegramObject
from services import get_manager_id
from utils.states import ClientMainStates


class SlowpokeMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        try:
            manager_id = await get_manager_id(event.from_user.id)
        except AttributeError:
            pass
        else:
            if event.data == "back_to_menu":
                if (FSMContext.get_state(event.from_user.id) not in
                        [ClientMainStates.in_support_chat, ClientMainStates.in_main_menu]):
                    await self.bot.send_message(manager_id, f"⚠️ Клиент {event.from_user.full_name} "
                                                            f"прервал заполнение формы. "
                                                            f"Номер его телеграмма: {event.from_user.id}")
        return await handler(event, data)
