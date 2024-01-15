import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import settings
from utils.sql import Database


path =('media\\images\\logo_bot.png')
storage = MemoryStorage()
bot = Bot(settings.TOKEN_API, parse_mode="html")
dp = Dispatcher(bot, storage=storage)
db = Database("db.db")