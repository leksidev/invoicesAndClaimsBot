from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.main_menu import UserStates
from models.claims_orm import ClaimsOrm
from repositories.claim import ClaimRepository
from repositories.invoice import InvoiceRepository
from repositories.users import UsersRepository

router = Router()


class CreateClaim(StatesGroup):
    waiting_invoice_id = State()
    waiting_email = State()
    waiting_description = State()
    waiting_amount = State()
    waiting_docs = State()
    done = State()


@router.message(F.text == "Зарегистрировать претензию")
async def create_claim(message: Message, state: FSMContext):
    await state.set_state(CreateClaim.waiting_invoice_id)
    builder = InlineKeyboardBuilder()
    users_invoices = await InvoiceRepository.get_all_user_invoices(message.from_user.id)
    for invoice_id in users_invoices:
        builder.add(InlineKeyboardButton(
            text=str(invoice_id),
            callback_data=str(invoice_id))
        )
    await message.answer("Введите номер накладной:", reply_markup=builder.as_markup())
    await state.update_data(invoice_id="")


@router.callback_query(F.data, CreateClaim.waiting_invoice_id)
async def create_claim(callback: CallbackQuery, state: FSMContext):
    await state.update_data(invoice_id=int(callback.data))
    await state.set_state(CreateClaim.waiting_email)
    await callback.message.answer("Введите ваш email:")
    await state.update_data(email="")


@router.message(F.text, CreateClaim.waiting_invoice_id)
async def incorrect_invoice_id(message: Message):
    await message.answer("Некорректный номер накладной. Пришлите, пожалуйста, номер накладной, например, 12345.")


@router.message(F.text.regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'), CreateClaim.waiting_email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(CreateClaim.waiting_description)
    await message.answer("Введите описание претензии:")
    await state.update_data(description="")


@router.message(F.text, CreateClaim.waiting_email)
async def incorrect_weight(message: Message):
    await message.answer("Некорректная почта. Пришлите, пожалуйста, почту, например, user@mail.ru.")


@router.message(F.text, CreateClaim.waiting_description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateClaim.waiting_amount)
    await message.answer("Введите сумму претензии:")
    await state.update_data(amount="")


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), CreateClaim.waiting_amount)
async def get_amount(message: Message, state: FSMContext):
    await state.update_data(amount=float(message.text))
    await state.set_state(CreateClaim.waiting_docs)
    await message.answer("Прикрепите документы:")
    await state.update_data(docs="")


@router.message(F.text, CreateClaim.waiting_amount)
async def incorrect_amount(message: Message):
    await message.answer("Некорректная сумма. Пришлите, пожалуйста, сумму цифрами, например, 2000 или 2000,50.")


@router.message(F.photo, CreateClaim.waiting_docs)
async def get_docs(message: Message, state: FSMContext):
    await state.update_data(docs=message.text)
    await state.update_data(client_id=message.from_user.id)
    claim = await state.get_data()
    new_id = await ClaimRepository.add_claim(ClaimsOrm(**claim))
    await message.answer(f"Ваша претензия номер: {new_id}\n\n"
                         f"номер накладной:{claim['invoice_id']}\n"
                         f"описание претензии:{claim['description']}\n"
                         f"сумма претензии:{claim['amount']}\n"
                         f"email:{claim['email']}"
                         f"фото:{claim['docs']}")

    await state.set_state(CreateClaim.done)

    await state.set_state(UserStates.in_main_menu)
    await message.answer("Зарегистрировано!", reply_markup=ReplyKeyboardRemove())


@router.message(F.text, CreateClaim.waiting_docs)
async def incorrect_docs(message: Message):
    await message.answer("Некорректные документы. Пришлите, пожалуйста, документы, например, фото, "
                         "которые вы хотите прикрепить.")
