from aiogram.fsm.state import StatesGroup, State


class ManagerMainStates(StatesGroup):
    in_main_menu = State()
    in_chat_list = State()
    in_active_chat = State()
    in_claims_list = State()


class ClientMainStates(StatesGroup):
    in_main_menu = State()
    in_support_chat = State()
    sent_support_chat_request = State()
    creating_invoice = State()
    creating_claim = State()


class ClientSubStates(StatesGroup):
    ADDING_INVOICE_DESCRIPTION = State()
    ADDING_INVOICE_WEIGHT = State()
    ADDING_INVOICE_HEIGHT = State()
    ADDING_INVOICE_WIDTH = State()
    ADDING_INVOICE_LENGTH = State()
    ADDING_INVOICE_FROM_ADDRESS = State()
    ADDING_INVOICE_TO_ADDRESS = State()
    ADDING_INVOICE_PAY_METHOD = State()
    ADDING_INVOICE_DONE = State()


class CreateClaim(StatesGroup):
    waiting_invoice_id = State()
    waiting_email = State()
    waiting_description = State()
    waiting_amount = State()
    waiting_docs = State()
    done = State()
