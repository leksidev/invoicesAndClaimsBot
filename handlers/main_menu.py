import os

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from handlers.create_invoice import ClientSubStates
from keyboards.chat_keyboard import close_chat_keyboard
from keyboards.client_keyboard import client_main_keyboard
from keyboards.manager_keyboard import manager_main_keyboard
from keyboards.service_keys import inline_back_to_menu

from models.model import Client, ChatRequest

from services import get_manager_id, add_client, get_opened_chats, send_chat_request, get_all_invoices_by_client, \
    close_chat, check_chat_status

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
async def chat_with_manager(message: Message):
    manager_id = await get_manager_id(message.chat.id)
    chat_request = ChatRequest(client_id=message.from_user.id, manager_id=manager_id)
    await send_chat_request(chat_request)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Открыть чат", callback_data=f"чат id: {chat_request.client_id}"))
    await bot.send_message(manager_id, f"Запрос от {message.from_user.full_name}", reply_markup=builder.as_markup())
    await message.answer(f"Менеджер получил ваш запрос. \n "
                         f"Когда менеджер подключится к чату, вам придет уведомление",
                         reply_markup=inline_back_to_menu)


@router.callback_query(
    F.data.startswith("чат id:")
)
async def open_chat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManagerMainStates.in_active_chat)
    chat_id = int(callback.data.split(":")[1])
    await callback.message.answer("Чат с клиентом открыт.")
    await state.update_data(chat_id=chat_id)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отклонить запрос", callback_data="close_chat"))
    builder.add((InlineKeyboardButton(text="Подключиться к чату", callback_data="connect_to_chat")))
    await bot.send_message(chat_id, "Менеджер подключился к чату", reply_markup=builder.as_markup())


@router.callback_query(F.data == "connect_to_chat")
async def connect_to_chat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientMainStates.in_support_chat)
    await state.update_data(chat_id=callback.from_user.id)
    await bot.send_message(callback.from_user.id, "Отправьте ваше сообщение", reply_markup=close_chat_keyboard)


@router.message(F.text, ClientMainStates.in_support_chat)
async def send_to_manager(message: Message, state: FSMContext):
    client_id = message.chat.id
    chat_status = await check_chat_status(client_id)
    if chat_status:
        manager_id = await get_manager_id(client_id)
        await bot.send_message(manager_id, message.text, reply_markup=close_chat_keyboard)
    else:
        await message.answer("Невозможно отправить сообщение. Пожалуйста, переподключитесь к чату.")
        await state.set_state(ClientMainStates.in_main_menu)


@router.callback_query(F.data == "close_chat", ManagerMainStates.in_active_chat)
async def finish_chat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManagerMainStates.in_main_menu)
    chat_id = await state.get_data()
    await close_chat(chat_id["chat_id"])
    await bot.send_message(chat_id["chat_id"], "Чат завершен.")
    await callback.message.answer("Чат завершен. Вы вернулись в главное меню.")


@router.callback_query(F.data == "close_chat", ClientMainStates.in_support_chat)
@router.callback_query(F.data == "close_chat", ClientMainStates.in_main_menu)
async def finish_chat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientMainStates.in_main_menu)
    client_id = callback.from_user.id
    manager_id = await get_manager_id(client_id)
    await close_chat(client_id)
    await bot.send_message(manager_id, "Чат завершен.")
    await callback.message.answer("Чат завершен. Вы вернулись в главное меню.")


@router.message(F.text, ManagerMainStates.in_active_chat)
async def send_message(message: Message, state: FSMContext):
    chat_id = await state.get_data()
    is_chat_opened = await check_chat_status(chat_id["chat_id"])
    if is_chat_opened:
        await bot.send_message(chat_id["chat_id"], message.text, reply_markup=close_chat_keyboard)
    else:
        await message.answer("Невозможно отправить сообщение. Клиент завершил чат.")
        await state.set_state(ManagerMainStates.in_main_menu)


@router.message(F.text == "Чаты с клиентами", ManagerMainStates.in_main_menu)
async def get_chats(message: Message, state: FSMContext):
    await state.set_state(ManagerMainStates.in_chat_list)
    chats = await get_opened_chats()
    if chats:
        for chat in chats:
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Подключиться", callback_data=f"чат id: {chat.client_id}"))
            await message.answer(f"Номер чата: {chat.id}", reply_markup=builder.as_markup())
        await message.answer("-", reply_markup=inline_back_to_menu)
    else:
        await message.answer("В базе нет ни одного чата. Вы вернулись в главное меню.")
        await state.set_state(ManagerMainStates.in_main_menu)


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
async def in_main_menu(message: Message):
    user_id = message.from_user.id
    manager = await if_manager(user_id)
    greeting_message = f"Здравствуйте, {message.from_user.first_name}. Выберите действие:"

    if manager:
        reply_markup = manager_main_keyboard
    else:
        reply_markup = client_main_keyboard

    await message.answer(greeting_message, reply_markup=reply_markup)
