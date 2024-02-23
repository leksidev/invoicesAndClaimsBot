from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards.client_keyboard import pay_keyboard, decision_keyboard, client_main_keyboard
from keyboards.service_keys import inline_back_to_menu
from models.model import Invoice
from services import add_invoice
from utils.states import ClientSubStates, ClientMainStates

router = Router()





@router.message(F.text, ClientSubStates.ADDING_INVOICE_DESCRIPTION)
async def get_invoice_weight(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_WEIGHT)
    await message.answer("Введите вес груза в килограммах:", reply_markup=inline_back_to_menu)
    await state.update_data(weight="")


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), ClientSubStates.ADDING_INVOICE_WEIGHT)
async def get_invoice_size(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_HEIGHT)
    await message.answer("Введите высоту груза в см:", reply_markup=inline_back_to_menu)
    await state.update_data(height="")


@router.message(F.text, ClientSubStates.ADDING_INVOICE_WEIGHT)
async def incorrect_weight(message: Message):
    await message.answer("Некорректный вес. Пришлите, пожалуйста, вес груза цифрами, например, 5 или 12.",
                         reply_markup=inline_back_to_menu)


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), ClientSubStates.ADDING_INVOICE_HEIGHT)
async def get_invoice_size(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_WIDTH)
    await message.answer("Введите ширину груза в см:", reply_markup=inline_back_to_menu)
    await state.update_data(width="")


@router.message(F.text, ClientSubStates.ADDING_INVOICE_HEIGHT)
async def incorrect_height(message: Message):
    await message.answer("Некорректная высота. Пришлите, пожалуйста, высоту груза цифрами, "
                         "например, 5 или 120.", reply_markup=inline_back_to_menu)


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), ClientSubStates.ADDING_INVOICE_WIDTH)
async def get_invoice_length(message: Message, state: FSMContext):
    await state.update_data(width=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_LENGTH)
    await message.answer("Введите длину груза в см:", )
    await state.update_data(length="")


@router.message(F.text, ClientSubStates.ADDING_INVOICE_WIDTH)
async def incorrect_width(message: Message):
    await message.answer("Некорректная ширина. Пришлите, пожалуйста, ширину груза цифрами, "
                         "например, 5 или 120.", reply_markup=inline_back_to_menu)


@router.message(F.text, F.text.regexp(r'^\d+(\.\d{1,2})?$'), ClientSubStates.ADDING_INVOICE_LENGTH)
async def get_invoice_from_address(message: Message, state: FSMContext):
    await state.update_data(length=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_FROM_ADDRESS)
    await message.answer("Введите адрес отправителя:", reply_markup=inline_back_to_menu)
    await state.update_data(from_address="")


@router.message(F.text, ClientSubStates.ADDING_INVOICE_FROM_ADDRESS)
async def get_invoice_to_address(message: Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_TO_ADDRESS)
    await message.answer("Введите адрес получателя:", reply_markup=inline_back_to_menu)
    await state.update_data(to_address="")


@router.message(F.text, ClientSubStates.ADDING_INVOICE_TO_ADDRESS)
async def get_invoice_pay_method(message: Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(ClientSubStates.ADDING_INVOICE_PAY_METHOD)
    await message.answer("Выберите способ оплаты", reply_markup=pay_keyboard)



@router.callback_query(F.data.in_(["Карта", "Наличные"]), ClientSubStates.ADDING_INVOICE_PAY_METHOD)
async def save_invoice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pay_method=callback.data)
    await state.update_data(client_id=callback.from_user.id)
    invoice = await state.get_data()
    await callback.message.answer(f'Ваша накладная: \n\n'
                                  f'описание груза: {invoice["description"]}\n'
                                  f'вес: {invoice["weight"]}\n'
                                  f'размеры: {invoice["height"]}x{invoice["width"]}x{invoice["length"]}\n'
                                  f'адрес отправителя: {invoice["from_address"]}\n'
                                  f'адрес получателя: {invoice["to_address"]}\n'
                                  f'способ оплаты: {invoice["pay_method"]}\n',
                                  reply_markup=decision_keyboard)
    await state.set_state(ClientSubStates.ADDING_INVOICE_DONE)


@router.callback_query(F.data == "save")
async def save_invoice(callback: CallbackQuery, state: FSMContext):
    invoice = await state.get_data()
    new_id = await add_invoice(Invoice(**invoice))
    await callback.message.answer(f'Ваша накладная #{new_id} сохранена в базе данных\n\n'
                                  f'Вы вышли в главное меню',
                                  reply_markup=client_main_keyboard)
    await state.clear()
    await state.set_state(ClientMainStates.in_main_menu)

