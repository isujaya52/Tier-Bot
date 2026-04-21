from config import bot
import json
import re
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from BOT.all_cmd import cek_tier
from BOT.seasonV import __season__ as season

FILE = '/app/BOT/JSON/data.json' 
SEASON_PATH = 'BOT/seasonV.py'


async def update_season(new_season):
    with open(SEASON_PATH, 'r') as f:
        content = f.read()
    content = re.sub(
        r'(__season__\s*=\s*[\'"])([^\'"]+)([\'"])',
        r'\g<1>' + new_season + r'\g<3>',
        content
    )
    with open(SEASON_PATH, 'w') as f:
        f.write(content)


async def save(data):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def reset_season():
    new_season = str(int(season) + 1)
    await update_season(new_season)

    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for chatid in list(data.keys()):
        user_data = data[chatid]
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['point'], reverse=True)
        pesan = f"<b>RESET SEASON</b>\n\n<b>DAFTAR TIER TERTINGGI SEASON {season}:</b>\n"
        for i, (userid, userdata) in enumerate(sorted_users[:10], start=1):
            try:
                nama = (await bot.get_chat(int(userid))).first_name
            except Exception:
                nama = 'Anon'
            mention = f"<a href='tg://user?id={userid}'>{nama}</a>"
            point = userdata['point']
            tier, star = await cek_tier(point)
            pesan += f"{i}.{mention} => {point} {tier} ×{star}⭐\n"
        pesan += f"\nSilahkan push lagi tiermu! Semoga beruntung di SEASON {new_season}"
        try:
            await bot.send_message(int(chatid), pesan)
        except Exception:
            pass
        del data[chatid]

    await save(data)


reset = AsyncIOScheduler(timezone="Asia/Jakarta")
reset.add_job(reset_season, trigger="cron", minute=0, hour=0, day=1)
