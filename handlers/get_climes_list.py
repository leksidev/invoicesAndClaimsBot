import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv

from handlers.main_menu import ManagerMainStates
from keyboards.manager_keyboard import manager_main_keyboard
from keyboards.service_keys import inline_back_to_menu
from services import get_all_claims

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

router = Router()
bot = Bot(token=os.environ["BOT_TOKEN"])


# @router.message(F.text == "Посмотреть претензии")
# async def get_climes_list(message: Message):
#     claims = await ClaimRepository.get_all_claims()
#     if claims:
#         for claim in claims:
#             await message.answer(f"Номер претензии: {claim.claim_id}\n"
#                                  f"описание претензии: {claim.description}\n"
#                                  f"сумма претензии: {claim.amount}\n"
#                                  f"email:{claim.email}")
#     else:
#         await message.answer("✅ В базе нет нерассмотренных претензий")


@router.message(F.text == "Посмотреть претензии", ManagerMainStates.in_main_menu)
async def get_claims_list(message: Message, state: FSMContext):
    await state.set_state(ManagerMainStates.in_claims_list)
    await show_page(message, 1, 2)
    await message.answer("Для выхода нажмите кнопку", reply_markup=inline_back_to_menu)


async def show_page(message, page_number, page_size):
    claims = await get_all_claims()

    if claims:
        total_pages = (len(claims) + page_size - 1) // page_size
        start_index = (page_number - 1) * page_size
        end_index = min(start_index + page_size, len(claims))
        claims_page = claims[start_index:end_index]

        output = ""
        for claim in claims_page:
            output += format_claim(claim) + "\n"

        keyboard = generate_pagination_keyboard(total_pages)

        await message.answer(text=output, reply_markup=keyboard)
    else:
        await message.answer("✅ В базе нет нерассмотренных претензий")


async def send_page(message, claims, page_number, page_size):
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, len(claims))
    claims_page = claims[start_index:end_index]

    for claim in claims_page:
        await message.answer(format_claim(claim))


async def paginate(message, page_number, page_size):
    claims = await get_all_claims()
    await send_page(message, claims, page_number, page_size)


@router.callback_query(F.data.startswith("page:"))
async def change_page(call: CallbackQuery):
    page_number = int(call.data.split(":")[1])
    await paginate(call.message, page_number, 2)
    await call.answer()


def generate_pagination_keyboard(total_pages) -> InlineKeyboardMarkup:
    if total_pages > 1:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=str(page_number), callback_data=f"page:{page_number}")
             for page_number in range(1, total_pages + 1)]], resize_keyboard=True)
        return keyboard
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1", callback_data=f"page:1")]],
                                    resize_keyboard=True)


def format_claim(claim):
    return (f"Номер претензии: {claim.claim_id}\n"
            f"Описание претензии: {claim.description}\n"
            f"Сумма претензии: {claim.amount}\n"
            f"Email: {claim.email}\n\n")


@router.callback_query(ManagerMainStates.in_claims_list, F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManagerMainStates.in_main_menu)
    await callback.message.answer("Вы вернулись в меню", reply_markup=manager_main_keyboard)
