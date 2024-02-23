from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

back_to_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Вернуться в меню")]],
    resize_keyboard=True, )

inline_back_to_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=f"Нажмите, чтобы вернуться в меню",
                             callback_data="back_to_menu")]])
