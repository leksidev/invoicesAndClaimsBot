from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main_menu_buttons = ['Сформировать накладную', 'Зарегистрировать претензию', 'Связаться с менеджером']

client_main_keyboard = ReplyKeyboardMarkup(keyboard=
                                           [[KeyboardButton(text=button_name)] for button_name in main_menu_buttons],
                                           one_time_keyboard=False,
                                           resize_keyboard=True,
                                           input_field_placeholder='Выберите действие: ',
                                           is_persistent=True,
                                           )

decision_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Cохранить", callback_data="save"), InlineKeyboardButton(text="Отмена",
                                                                                        callback_data="back_to_menu")]
])

pay_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Карта", callback_data="Карта"),
     InlineKeyboardButton(text="Наличные", callback_data="Наличные")]
])
