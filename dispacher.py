# Modules

from aiogram import Bot, Dispatcher
import logging
from config import token
from sqlighter import SQLighter
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Log

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

# Default Variebles

bot = Bot(token, parse_mode="html")
dp = Dispatcher(bot, storage=MemoryStorage())
db = SQLighter("db.db")
