import os

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from handlers.create_invoice import ClientSubStates
from keyboards.client_keyboard import client_main_keyboard
from keyboards.manager_keyboard import manager_main_keyboard
from keyboards.service_keys import inline_back_to_menu

from models.model import Client, ChatRequest

from services import get_manager_id, add_client, get_opened_chats, send_chat_request, get_all_invoices_by_client

from utils.check_role import if_manager
from utils.states import ManagerMainStates, ClientMainStates, CreateClaim

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

router = Router()
bot = Bot(token=os.environ["BOT_TOKEN"])


@router.callback_query(F.data == "back_to_menu", CreateClaim.waiting_invoice_id)
@router.callback_query(F.data == "back_to_menu", CreateClaim.waiting_email)
@router.callback_query(F.data == "back_to_menu", CreateClaim.waiting_amount)
@router.callback_query(F.data == "back_to_menu", CreateClaim.waiting_description)
@router.callback_query(F.data == "back_to_menu", CreateClaim.waiting_docs)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_DESCRIPTION)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_WEIGHT)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_HEIGHT)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_WIDTH)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_LENGTH)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_FROM_ADDRESS)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_TO_ADDRESS)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_PAY_METHOD)
@router.callback_query(F.data == "back_to_menu", ClientSubStates.ADDING_INVOICE_DONE)
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ClientMainStates.in_main_menu)
    await callback.message.answer("Вы вернулись в главное меню", reply_markup=client_main_keyboard)


@router.message(F.text == "Зарегистрировать претензию", ClientMainStates.in_main_menu)
async def create_claim(message: Message, state: FSMContext):
    await state.set_state(CreateClaim.waiting_invoice_id)
    builder = InlineKeyboardBuilder()
    users_invoices = await get_all_invoices_by_client(message.from_user.id)
    if users_invoices:
        for invoice_id in users_invoices:
            builder.add(InlineKeyboardButton(
                text=str(invoice_id),
                callback_data=str(invoice_id))
            )
        await message.answer("Выберите номер накладной:", reply_markup=builder.as_markup())

    else:
        await message.answer("Не удалось найти список накладных. "
                             "Пришлите номер накладной для оформления претензии, пожалуйста.",
                             reply_markup=inline_back_to_menu)
    await state.update_data(invoice_id="")


@router.message(F.text == "Сформировать накладную", ClientMainStates.in_main_menu)
async def create_invoice(message: Message, state: FSMContext):
    await state.set_state(ClientSubStates.ADDING_INVOICE_DESCRIPTION)
    await state.update_data(description="")
    await message.answer("Введите описание груза:", reply_markup=inline_back_to_menu)


@router.message(F.text == "Связаться с менеджером", ClientMainStates.in_main_menu)
async def chat_with_manager(message: Message, state: FSMContext):
    manager_id = await get_manager_id(message.chat.id)
    await send_chat_request(ChatRequest(client_id=message.from_user.id, manager_id=manager_id))
    await bot.send_message(manager_id, "Запрос на общение с клиентом!")


@router.message(F.text == "Чаты с клиентами", ManagerMainStates.in_main_menu)
async def get_chats(message: Message, state: FSMContext):
    await state.set_state(ManagerMainStates.in_chat_list)
    chats = await get_opened_chats()
    if chats:
        for chat in chats:
            await message.answer(f"Номер чата: {chat.id}")
        await message.answer("", reply_markup=inline_back_to_menu)
    else:
        await message.answer("В базе нет ни одного чата!", reply_markup=inline_back_to_menu)


@router.callback_query(
    ManagerMainStates.in_chat_list or ManagerMainStates.in_active_chat or ManagerMainStates.in_claims_list,
    F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManagerMainStates.in_main_menu)
    await callback.message.answer("Вы вернулись в главное меню", reply_markup=manager_main_keyboard)


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    manager_id = int(os.environ["ADMIN_ID"])
    user_id = message.from_user.id
    manager = await if_manager(user_id)

    if manager:
        await message.answer("Вы авторизованы как менеджер!", reply_markup=manager_main_keyboard)
        await state.set_state(ManagerMainStates.in_main_menu)
    else:
        try:
            await add_client(Client(telegram_id=user_id, manager_id=manager_id))
        except IntegrityError:
            pass
        finally:
            await state.set_state(ClientMainStates.in_main_menu)
            await message.answer(f"Здравствуйте, {message.from_user.first_name}. Выберите действие:",
                                 reply_markup=client_main_keyboard)


@router.message(ClientMainStates.in_main_menu or ManagerMainStates.in_main_menu)
async def in_main_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    manager = await if_manager(user_id)
    greeting_message = f"Здравствуйте, {message.from_user.first_name}. Выберите действие:"

    if manager:
        reply_markup = manager_main_keyboard
    else:
        reply_markup = client_main_keyboard

    await message.answer(greeting_message, reply_markup=reply_markup)
