from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError

from keyboards.client_keyboard import client_main_keyboard
from keyboards.manager_keyboard import manager_main_keyboard
from models.clients_orm import ClientsOrm
from repositories.users import UsersRepository

from utils.check_role import if_manager


class UserStates(StatesGroup):
    in_main_menu = State()


router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    manager = await if_manager(message.from_user.id)
    if manager:

        await message.answer("Вы авторизованы как менеджер!", reply_markup=manager_main_keyboard)

    else:

        await UsersRepository.add_client(ClientsOrm(telegram_id=message.from_user.id, chat_id=message.chat.id))

        await message.answer(f"Здравствуйте, {message.from_user.first_name}. Выберите действие:",
                             reply_markup=client_main_keyboard)
    await state.set_state(UserStates.in_main_menu)


@router.message(UserStates.in_main_menu)
async def in_main_menu(message: Message, state: FSMContext):
    manager = await if_manager(message.from_user.id)
    if manager:
        await message.answer("Выберите действие:", reply_markup=manager_main_keyboard)
    else:
        await message.answer(f"Здравствуйте, {message.from_user.first_name}. Выберите действие:",
                             reply_markup=client_main_keyboard)
