from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

manager_menu_buttons = ['Чаты с клиентами', 'Претензии от клиентов', 'Уведомления об обращении клиента к боту']

manager_main_keyboard = ReplyKeyboardMarkup(keyboard=
                                            [[KeyboardButton(text=button_name)] for button_name in
                                             manager_menu_buttons],
                                            one_time_keyboard=False,
                                            resize_keyboard=True,
                                            input_field_placeholder='Выберите действие: ',
                                            is_persistent=True)
