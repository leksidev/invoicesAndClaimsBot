from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from repositories.invoice import InvoiceRepository

decision_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Cохранить", callback_data="save"), InlineKeyboardButton(text="Отмена", callback_data="cancel")]
])

pay_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Картой", callback_data="card"),
     InlineKeyboardButton(text="Наличными", callback_data="cash")]
])
