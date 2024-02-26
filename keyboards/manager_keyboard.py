from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

manager_menu_buttons = ['Чаты с клиентами', 'Посмотреть претензии']

manager_main_keyboard = ReplyKeyboardMarkup(keyboard=
                                            [[KeyboardButton(text=button_name)] for button_name in
                                             manager_menu_buttons],
                                            one_time_keyboard=False,
                                            resize_keyboard=True,
                                            input_field_placeholder='Выберите действие: ',
                                            is_persistent=True)

exit_to_main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вернуться в меню')]],
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
