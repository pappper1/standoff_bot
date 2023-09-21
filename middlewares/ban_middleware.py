from aiogram import Dispatcher
from aiogram.dispatcher.handler import CancelHandler  
from aiogram.dispatcher.middlewares import BaseMiddleware  
from aiogram.types import Message, CallbackQuery
from loader import db

class UserBannedMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        users = db.get_banned_users()
        for user in users:
            if message.from_user.id == user[0]:
                await message.answer(
                    '<b> Ваш аккаунт заблокирован!</b>'
                )
                raise CancelHandler

    async def on_process_callback_query(self, call: CallbackQuery, data: dict):
        users = db.get_banned_users()
        for user in users:
            if call.from_user.id == user[0]:
                await call.answer(
                    ' Ваш аккаунт заблокирован!',
                    show_alert=True
                )
                raise CancelHandler
        

def setup_ban_middleware(dp: Dispatcher):
    dp.middleware.setup(UserBannedMiddleware())

def setup_middlewares(dp: Dispatcher):
    setup_ban_middleware(dp)