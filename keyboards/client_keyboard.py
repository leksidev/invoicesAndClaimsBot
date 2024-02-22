from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_buttons = ['Сформировать накладную', 'Зарегистрировать претензию', 'Связаться с менеджером']

client_main_keyboard = ReplyKeyboardMarkup(keyboard=
                                           [[KeyboardButton(text=button_name)] for button_name in main_menu_buttons],
                                           one_time_keyboard=False,
                                           resize_keyboard=True,
                                           input_field_placeholder='Выберите действие: ',
                                           is_persistent=True,
                                           )
