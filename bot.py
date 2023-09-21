import data.config as cfg
from loader import dp, bot, db, path
from aiogram import executor, types
from loguru import logger
import keyboards.inline as ikb
from media.texts.captions import *
from utils.other_utils import *
import handlers
from middlewares.ban_middleware import setup_middlewares


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.from_user.id == cfg.ADMIN:
        with open(path, "rb") as pic:
            await bot.send_photo(chat_id=message.from_user.id, photo=pic, caption="Добро пожаловать в админ-панель!", reply_markup=ikb.admin())
    
    else:
        if not db.user_exists(message.from_user.id):
            try:
                db.add_user(message.from_user.id, message.from_user.username, date)
            
            except Exception as e:
                logger.error(e)

            db.update_user_count()
        
            with open(path, "rb") as pic:
                await bot.send_photo(chat_id=message.from_user.id, photo=pic, caption=start_message, reply_markup=ikb.start_ikb())

        else:         
            with open(path, "rb") as pic:
                await bot.send_photo(chat_id=message.from_user.id, photo=pic, caption=start_message, reply_markup=ikb.start_ikb())


async def on_startup(_):
    logger.info("Бот запущен!")
    setup_middlewares(dp)
    db.create_tables()

async def on_shutdown(_):
    logger.info("Бот отключен!")

if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup, on_shutdown= on_shutdown)