from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove


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


@router.callback_query(F.data == "create_invoice")
async def create_invoice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description="")
    await state.set_state(CreateInvoice.waiting_description)
    await callback.message.answer("Введите описание груза")
    await callback.answer()


@router.message(F.text, CreateInvoice.waiting_description)
async def get_invoice_weight(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateInvoice.waiting_weight)
    await message.answer("Введите вес груза", reply_markup=ReplyKeyboardRemove())
    await state.update_data(weight="")


@router.message(F.text, lambda message: message.text.isdigit(), CreateInvoice.waiting_weight)
async def get_invoice_size(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(CreateInvoice.waiting_size)
    await message.answer("Введите размер груза")
    await state.update_data(size="")


@router.message(F.text, lambda message: message.text.isdigit(), CreateInvoice.waiting_size)
async def get_invoice_from_address(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(CreateInvoice.waiting_from_address)
    await message.answer("Введите адрес отправителя")
    await state.update_data(from_address="")


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
    await message.answer("Выберите способ оплаты")


@router.message(F.text, CreateInvoice.waiting_pay_method)
async def save_invoice(message: Message, state: FSMContext):
    await state.update_data(pay_method=message.text)
    invoice = await state.get_data()
    new_id = await InvoiceRepository.add_invoice(InvoicesOrm(**invoice))
    await message.answer(f'Ваша накладная: {invoice}')
    await message.answer(f'Номер накладной: {new_id}')
    await state.set_state(CreateInvoice.done)
    await state.clear()
