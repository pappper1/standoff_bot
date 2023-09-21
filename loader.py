import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import data.config as cfg
from utils.sql import Database


path =('media\\images\\logo_bot.png')
storage = MemoryStorage()
bot = Bot(cfg.TOKEN_API, parse_mode="html")
dp = Dispatcher(bot, storage=storage)
db = Database("db.db")