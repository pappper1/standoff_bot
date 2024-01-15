from aiogram.dispatcher.filters.state import State, StatesGroup


class AddNewGame(StatesGroup):
    bet=State()
    description=State()


class Arbitration(StatesGroup):
    proofs=State()


class Spam(StatesGroup):
    spam=State()


class Ban(StatesGroup):
    ban=State()


class Unban(StatesGroup):
    unban=State()


class WithDraw(StatesGroup):
    info=State()
    amount=State()
    acceptation=State()


class AddBalance(StatesGroup):
    user=State()
    amount=State()
    confirmation=State()


class CashIn(StatesGroup):
    amount=State()
    confirmation = State()