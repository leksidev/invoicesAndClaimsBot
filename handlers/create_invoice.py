from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from handlers.main_menu import UserStates
from keyboards.create_invoice_keyboard import pay_keyboard
from models.invoice_orm import InvoicesOrm
from repositories.invoice import InvoiceRepository

router = Router()


class CreateInvoice(StatesGroup):
    waiting_description = State()
    waiting_weight = State()
    waiting_size = State()
    waiting_from_address = State()
    waiting_to_address = State()
    waiting_pay_method = State()
    done = State()


@router.message(F.text == "Сформировать накладную", UserStates.in_main_menu)
async def create_invoice(message: Message, state: FSMContext):
    await state.set_state(CreateInvoice.waiting_description)
    await state.update_data(description="")
    await message.answer("Введите описание груза:")


@router.message(F.text, CreateInvoice.waiting_description)
async def get_invoice_weight(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateInvoice.waiting_weight)
    await message.answer("Введите вес груза в килограммах:")
    await state.update_data(weight="")


@router.message(F.text, lambda message: message.text.isdigit(), CreateInvoice.waiting_weight)
async def get_invoice_size(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(CreateInvoice.waiting_size)
    await message.answer("Введите размер груза")
    await state.update_data(size="")


@router.message(F.text, CreateInvoice.waiting_weight)
async def incorrect_weight(message: Message, state: FSMContext):
    await message.answer("Некорректный вес. Пришлите, пожалуйста, вес груза цифрами, например, 5 или 12.")


@router.message(F.text, lambda message: message.text.isdigit(), CreateInvoice.waiting_size)
async def get_invoice_from_address(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(CreateInvoice.waiting_from_address)
    await message.answer("Введите адрес отправителя")
    await state.update_data(from_address="")


@router.message(F.text, CreateInvoice.waiting_size)
async def incorrect_size(message: Message, state: FSMContext):
    await message.answer("Некорректный размер. Пришлите, пожалуйста, размер груза цифрами, например, 5 или 12.")


@router.message(F.text, CreateInvoice.waiting_from_address)
async def get_invoice_to_address(message: Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(CreateInvoice.waiting_to_address)
    await message.answer("Введите адрес получателя")
    await state.update_data(to_address="")


@router.message(F.text, CreateInvoice.waiting_to_address)
async def get_invoice_pay_method(message: Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(CreateInvoice.waiting_pay_method)
    await message.answer("Выберите способ оплаты", reply_markup=pay_keyboard)


@router.message(F.text == "Оплата наличными" or F.text == "Оплата картой", CreateInvoice.waiting_pay_method)
async def save_invoice(message: Message, state: FSMContext):
    await state.update_data(pay_method=message.text)
    await state.update_data(telegram_id=message.from_user.id)
    invoice = await state.get_data()
    new_id = await InvoiceRepository.add_invoice(InvoicesOrm(**invoice))
    await message.answer(f'Ваша накладная: \n\n'
                         f'описание груза: {invoice["description"]}\n'
                         f'вес: {invoice["weight"]}\n'
                         f'размер: {invoice["size"]}\n'
                         f'адрес отправителя: {invoice["from_address"]}\n'
                         f'адрес получателя: {invoice["to_address"]}\n'
                         f'способ оплаты: {invoice["pay_method"]}\n'
                         )
    await message.answer(f'Номер накладной: {new_id}')
    await state.set_state(CreateInvoice.done)
    await state.clear()
    await state.set_state(UserStates.in_main_menu)


@router.message(F.text, CreateInvoice.waiting_pay_method)
async def incorrect_pay_method(message: Message):
    await message.answer("Некорректный способ оплаты. "
                         "Выберите в меню или пришлите, пожалуйста, способ оплаты, например, Оплата наличными или "
                         "Оплата картой.")
