from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.main_menu import ClientMainStates
from keyboards.client_keyboard import client_main_keyboard
from keyboards.service_keys import inline_back_to_menu
from models.model import Claim
from services import add_claim
from services import get_all_invoices_by_client
from utils.states import CreateClaim

router = Router()


@router.message(F.text, lambda c: c.text.isdigit(), CreateClaim.waiting_invoice_id)
async def create_claim(message: Message, state: FSMContext):
    await state.update_data(invoice_id=int(message.text))
    await state.set_state(CreateClaim.waiting_email)
    await message.answer("Введите ваш email:")
    await state.update_data(email="")


@router.callback_query(F.data != "back_to_menu", CreateClaim.waiting_invoice_id)
async def create_claim(callback: CallbackQuery, state: FSMContext):
    await state.update_data(invoice_id=int(callback.data))
    await state.set_state(CreateClaim.waiting_email)
    await callback.message.answer("Введите ваш email:")
    await state.update_data(email="")


@router.message(F.text.regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'), CreateClaim.waiting_email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(CreateClaim.waiting_description)
    await message.answer("Введите описание претензии:", reply_markup=inline_back_to_menu)
    await state.update_data(description="")


@router.message(F.text, CreateClaim.waiting_email)
async def incorrect_weight(message: Message):
    await message.answer("Некорректная почта. Пришлите, пожалуйста, почту, например, user@mail.ru.",
                         reply_markup=inline_back_to_menu)


@router.message(F.text, CreateClaim.waiting_description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateClaim.waiting_amount)
    await message.answer("Введите сумму претензии:", reply_markup=inline_back_to_menu)
    await state.update_data(amount="")


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), CreateClaim.waiting_amount)
async def get_amount(message: Message, state: FSMContext):
    await state.update_data(amount=float(message.text))
    await state.set_state(CreateClaim.waiting_docs)
    await message.answer("Прикрепите документы:", reply_markup=inline_back_to_menu)
    await state.update_data(docs="")


@router.message(F.text, CreateClaim.waiting_amount)
async def incorrect_amount(message: Message):
    await message.answer("Некорректная сумма. Пришлите, пожалуйста, сумму цифрами, например, 2000 или 2000,50.",
                         reply_markup=inline_back_to_menu)


@router.message(CreateClaim.waiting_docs)
async def get_docs(message: Message, state: FSMContext):
    await state.update_data(docs=message.text)
    await state.update_data(client_id=message.from_user.id)
    claim_data = await state.get_data()
    claim = Claim(**claim_data)
    new_id = await add_claim(claim)
    await message.answer(f"Ваша претензия номер: {new_id}\n\n"
                         f"номер накладной:{claim.invoice_id}\n"
                         f"описание претензии:{claim.description}\n"
                         f"сумма претензии:{claim.amount}\n"
                         f"email:{claim.email}"
                         f"фото:{claim.docs}")

    await state.set_state(CreateClaim.done)

    await state.clear()
    await state.set_state(ClientMainStates.in_main_menu)
    await message.answer("Зарегистрировано!", reply_markup=client_main_keyboard)


@router.message(F.text, CreateClaim.waiting_docs)
async def incorrect_docs(message: Message):
    await message.answer("Некорректные документы. Пришлите, пожалуйста, документы, например, фото, "
                         "которые вы хотите прикрепить.", reply_markup=inline_back_to_menu)
