from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_to_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отменить")]],
    resize_keyboard=True)