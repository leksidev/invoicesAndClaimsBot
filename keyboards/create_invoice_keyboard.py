from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

pay_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Оплата картой')],
    [KeyboardButton(text='Оплата наличными')]
], resize_keyboard=True, input_field_placeholder='Выберите способ оплаты:')
