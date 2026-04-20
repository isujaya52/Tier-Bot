from config import bot, own
from functools import wraps


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
