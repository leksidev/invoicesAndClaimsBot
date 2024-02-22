from services import get_all_managers


async def if_manager(telegram_id: int) -> bool:
    all_managers = await get_all_managers()
    for manager in all_managers:
        if int(manager.telegram_id) == telegram_id:
            return True
    return False
