import asyncio
from telebot.async_telebot import AsyncTeleBot
import os

TOKEN = os.environ['TOKEN']
LOGS_ID = os.environ['LOGS_ID']
own = [5039288972, 1928677026]

bot = AsyncTeleBot(TOKEN, parse_mode='html')
