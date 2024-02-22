from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.main_menu import UserStates
from keyboards.create_invoice_keyboard import pay_keyboard, decision_keyboard
from keyboards.service_keys import back_to_menu
from models.invoice_orm import InvoicesOrm
from repositories.invoice import InvoiceRepository
from repositories.users import UsersRepository

router = Router()


class CreateInvoice(StatesGroup):
    waiting_description = State()
    waiting_weight = State()
    waiting_height = State()
    waiting_width = State()
    waiting_length = State()
    waiting_from_address = State()
    waiting_to_address = State()
    waiting_pay_method = State()
    done = State()


@router.message(F.text == "Сформировать накладную", UserStates.in_main_menu)
async def create_invoice(message: Message, state: FSMContext):
    await state.set_state(CreateInvoice.waiting_description)
    await state.update_data(description="")
    await message.answer("Введите описание груза:", reply_markup=back_to_menu)


@router.message(F.text, CreateInvoice.waiting_description)
async def get_invoice_weight(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateInvoice.waiting_weight)
    await message.answer("Введите вес груза в килограммах:", reply_markup=back_to_menu)
    await state.update_data(weight="")


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), CreateInvoice.waiting_weight)
async def get_invoice_size(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(CreateInvoice.waiting_height)
    await message.answer("Введите высоту груза в см:", reply_markup=back_to_menu)
    await state.update_data(height="")


@router.message(F.text, CreateInvoice.waiting_weight)
async def incorrect_weight(message: Message):
    await message.answer("Некорректный вес. Пришлите, пожалуйста, вес груза цифрами, например, 5 или 12.",
                         reply_markup=back_to_menu)


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), CreateInvoice.waiting_height)
async def get_invoice_size(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(CreateInvoice.waiting_width)
    await message.answer("Введите ширину груза в см:", reply_markup=back_to_menu)
    await state.update_data(width="")


@router.message(F.text, CreateInvoice.waiting_height)
async def incorrect_height(message: Message):
    await message.answer("Некорректная высота. Пришлите, пожалуйста, высоту груза цифрами, "
                         "например, 5 или 120.", reply_markup=back_to_menu)


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), CreateInvoice.waiting_width)
async def get_invoice_length(message: Message, state: FSMContext):
    await state.update_data(width=message.text)
    await state.set_state(CreateInvoice.waiting_length)
    await message.answer("Введите длину груза в см:", reply_markup=back_to_menu)
    await state.update_data(length="")


@router.message(F.text, CreateInvoice.waiting_width)
async def incorrect_width(message: Message, state: FSMContext):
    await message.answer("Некорректная ширина. Пришлите, пожалуйста, ширину груза цифрами, "
                         "например, 5 или 120.", reply_markup=back_to_menu)


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), CreateInvoice.waiting_length)
async def get_invoice_from_address(message: Message, state: FSMContext):
    await state.update_data(length=message.text)
    await state.set_state(CreateInvoice.waiting_from_address)
    await message.answer("Введите адрес отправителя:", reply_markup=back_to_menu)
    await state.update_data(from_address="")


@router.message(F.text, CreateInvoice.waiting_from_address)
async def get_invoice_to_address(message: Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(CreateInvoice.waiting_to_address)
    await message.answer("Введите адрес получателя:", reply_markup=back_to_menu)
    await state.update_data(to_address="")


@router.message(F.text, CreateInvoice.waiting_to_address)
async def get_invoice_pay_method(message: Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(CreateInvoice.waiting_pay_method)
    await message.answer("Выберите способ оплаты", reply_markup=pay_keyboard)


@router.callback_query(F.data.in_(["cash", "card"]), CreateInvoice.waiting_pay_method)
async def save_invoice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pay_method=callback.data)
    await state.update_data(client_id=callback.from_user.id)
    invoice = await state.get_data()
    await callback.message.answer(f'Ваша накладная: \n\n'
                                  f'описание груза: {invoice["description"]}\n'
                                  f'вес: {invoice["weight"]}\n'
                                  f'размеры: {invoice["height"]}x{invoice["width"]}x{invoice["length"]}\n'
                                  f'адрес отправителя: {invoice["from_address"]}\n'
                                  f'адрес получателя: {invoice["to_address"]}\n'
                                  f'способ оплаты: {invoice["pay_method"]}\n'
                                  , reply_markup=decision_keyboard)
    await state.set_state(CreateInvoice.done)


@router.callback_query(F.data == "save")
async def save_invoice(callback: CallbackQuery, state: FSMContext):
    invoice = await state.get_data()
    new_id = await InvoiceRepository.add_invoice(InvoicesOrm(**invoice))
    await callback.message.edit_text(f'Ваша накладная #{new_id} сохранена в базе данных\n\n',
                                     reply_markup=None)
    await state.clear()
    await state.set_state(UserStates.in_main_menu)


@router.callback_query(F.data == "cancel" or F.data == "back_to_menu")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UserStates.in_main_menu)


