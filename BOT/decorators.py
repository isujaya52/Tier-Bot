from config import bot, own
from functools import wraps
from config import LOGS_ID
import os
import traceback

def bot_admin(func):
    @wraps(func)
    async def wrapper(m, *args, **kwargs):
        if m.from_user.id in own or m.chat.type == 'private':
            return await func(m, *args, **kwargs)
        bot_info = await bot.get_me()
        member = await bot.get_chat_member(m.chat.id, bot_info.id)
        if member.status in ['creator', 'administrator']:
            return await func(m, *args, **kwargs)
        return await bot.reply_to(m, "Saya harus menjadi admin untuk menjalankan perintah ini.")
    return wrapper


def admins_only(func):
    @wraps(func)
    async def wrapper(m, *args, **kwargs):
        if m.from_user.id in own or m.chat.type == 'private':
            return await func(m, *args, **kwargs)
        member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        if member.status in ['creator', 'administrator']:
            return await func(m, *args, **kwargs)
        return await bot.reply_to(m, "Anda harus menjadi admin untuk melakukan ini.")
    return wrapper


def error_handler(func):
    @wraps(func)
    def wrapper(m, *args, **kwargs):
        try:
            return func(m, *args, **kwargs)
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"--- ERROR DETECTED ---\n{error_details}")
            
            log_text = (
                f"❌ **Error Terdeteksi!**\n\n"
                f"👤 User: {m.from_user.first_name} (@{m.from_user.username})\n"
                f"is Command/Text: `{m.text}`\n\n"
                f"⚠️ **Detail Error:**\n`{error_details[-3500:]}`" # Limit karakter agar tidak kena limit Telegram
            )
            
            try:
                bot.send_message(LOGS_ID, log_text, parse_mode='Markdown')
            except Exception as send_error:
                print(f"Gagal mengirim log ke channel: {send_error}")
                
    return wrapper
