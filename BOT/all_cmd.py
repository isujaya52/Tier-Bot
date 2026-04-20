from config import bot, own
import json
from BOT.decorators import admins_only, bot_admin
import asyncio
import importlib

season_module = importlib.import_module("BOT.seasonV")

FILE = 'BOT/JSON/data.json'
BACKUP = 'BOT/JSON/backup.json'


async def read():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(BACKUP, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except json.JSONDecodeError:
        with open(BACKUP, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data


async def save(data):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@bot.message_handler(commands=['start', 'help'])
async def start(m):
    data = await read()
    if m.chat.type == "private":
        jumlah = len(data)
        nama_bot = (await bot.get_me()).first_name
        await bot.reply_to(m,
            f"Hallo aku adalah {nama_bot}\n"
            f"Aku bisa menghitung jumlah pesan yang dikirim oleh user didalam group\n"
            f"Ayo cek Tiermu dengan mengetikan\n"
            f"- /mytier: Cek tiermu\n"
            f"- /grouptier: Cek daftar teratas tier group\n\n"
            f"CATATAN: Perintah ini hanya berlaku di group!! dan SEASON direset setiap sebulan sekali pada TGL 1\n"
            f"<b>Dipakai:</b> {jumlah} Group"
        )
    else:
        await bot.reply_to(m, "Ayo cek Tiermu dengan mengetikan /mytier")


@bot.message_handler(commands=['mytier'])
async def tierku(m):
    season = importlib.reload(season_module).__season__
    data = await read()
    if m.chat.type == "private":
        return await bot.reply_to(m, "Maaf kamu hanya bisa melihat tiermu didalam group!!")
    userid = str(m.from_user.id)
    chatid = str(m.chat.id)
    group = m.chat.title
    if chatid not in data or userid not in data[chatid]:
        return await bot.reply_to(m, "Kamu belum mempunyai Tier!!")
    nama = (await bot.get_chat(int(userid))).first_name
    point = data[chatid][userid]['point']
    tier = data[chatid][userid]['tier']
    star = data[chatid][userid]['star']
    stars = f"×{star}⭐" if star != 0 else ""
    msg = (
        f"<b>SEASON {season}</b>\n\n"
        f"Halo {nama},\n\n"
        f"Tier kamu di group {group} saat ini adalah <b>[ {tier} {stars} ]</b> "
        f"dengan total pesan terkirim: <b>{point}</b> Pesan.\n\n"
        f"Ayo tingkatkan aktifitas kamu di grup!"
    )
    await bot.reply_to(m, msg)


@bot.message_handler(commands=['grouptier'])
@bot_admin
@admins_only
async def grouptier(m):
    season = importlib.reload(season_module).__season__
    data = await read()
    if m.chat.type == "private":
        return await bot.reply_to(m, "Maaf kamu hanya bisa melihat daftar tier didalam group!!")
    chatid = str(m.chat.id)
    group = m.chat.title
    if chatid not in data:
        return await bot.reply_to(m, "Belum ada daftar peringkat!!")
    msg1 = await bot.reply_to(m, "<code>Sedang mengumpulkan data...</code>")
    sorted_users = sorted(data[chatid].items(), key=lambda x: x[1]['point'], reverse=True)
    result = f"<b>SEASON {season}</b>\n\n<b>DAFTAR TIER TERTINGGI</b> {group}\n\n"
    for i, (userid, userdata) in enumerate(sorted_users[:10], start=1):
        try:
            nama = (await bot.get_chat(int(userid))).first_name
        except Exception:
            nama = "Anon"
        point = userdata['point']
        tier = userdata['tier']
        star = userdata['star']
        mention = f"<a href='tg://user?id={userid}'>{nama}</a>"
        stars = f"×{star}⭐" if star != 0 else ""
        result += f"{i}.{mention} => {point} [ {tier} {stars} ]\n"
    await bot.edit_message_text(text=result, chat_id=m.chat.id, message_id=msg1.id)


@bot.message_handler(commands=['backup'])
async def backup_data(m):
    if int(m.from_user.id) not in own:
        return
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    await bot.reply_to(m, "<code>Data berhasil disalin ke file backup.</code>")


@bot.message_handler(commands=['copy'])
async def copy_backup(m):
    if int(m.from_user.id) not in own:
        return
    with open(BACKUP, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    await bot.reply_to(m, "<code>Data backup berhasil disalin ke file sumber.</code>")


@bot.message_handler(commands=['gcast'])
async def gcast(m):
    if int(m.from_user.id) not in own:
        return
    text = m.text.split(" ", 1)
    if len(text) == 1:
        return await bot.reply_to(m, "Masukan text!!")
    data = await read()
    msg = await bot.reply_to(m, "<code>Sedang menyiarkan pesan. . .</code>")
    sukses = 0
    pesan = "Sukses menyiarkan pesan ke:\n\n"
    for chatid in data:
        try:
            title = (await bot.get_chat(int(chatid))).title
            await bot.send_message(int(chatid), text[1])
            sukses += 1
            pesan += f"{sukses}.{title}\n"
        except Exception:
            pass
        await asyncio.sleep(2)
    await bot.edit_message_text(text=pesan, chat_id=m.chat.id, message_id=msg.id)


@bot.message_handler(func=lambda message: True)
async def save_point(m):
    if m.chat.type == "private":
        return
    data = await read()
    userid = str(m.from_user.id)
    chatid = str(m.chat.id)
    if chatid not in data:
        data[chatid] = {}
        await save(data)
    if userid in data[chatid]:
        old_star = data[chatid][userid]['star']
        point = data[chatid][userid]['point'] + 1
        new_tier, new_star = await cek_tier(point)
        data[chatid][userid]['point'] = point
        await save(data)
        if old_star != new_star:
            if new_tier != "Classic" and new_star == 0:
                return
            nama = (await bot.get_chat(int(userid))).first_name
            data[chatid][userid]['tier'] = new_tier
            data[chatid][userid]['star'] = new_star
            await save(data)
            msg = (
                f"SELAMAT {nama}\n\n"
                f"Kamu mengalami kenaikan\n"
                f"<b>TIER:</b> {new_tier} ×{new_star}⭐\n"
                f"<b>POINT:</b> {point}"
            )
            await bot.reply_to(m, msg)
    else:
        data[chatid][userid] = {"point": 1, "tier": "Classic", "star": 0}
        await save(data)


async def cek_tier(point):
    tiers = [
        (49,    "Classic",          0),
        (150,   "Wariorr III",      0),
        (300,   "Wariorr II",       150),
        (450,   "Wariorr I",        300),
        (650,   "Elite III",        450),
        (850,   "Elite II",         650),
        (1050,  "Elite I",          850),
        (1250,  "Master IV",        1050),
        (1450,  "Master III",       1250),
        (1650,  "Master II",        1450),
        (1850,  "Master I",         1650),
        (2100,  "Grandmaster V",    1850),
        (2350,  "Grandmaster IV",   2100),
        (2600,  "Grandmaster III",  2350),
        (2850,  "Grandmaster II",   2600),
        (3100,  "Grandmaster I",    2850),
        (3350,  "Epic V",           3100),
        (3600,  "Epic IV",          3350),
        (3850,  "Epic III",         3600),
        (4100,  "Epic II",          3850),
        (4350,  "Epic I",           4100),
        (4600,  "Legend V",         4350),
        (4850,  "Legend IV",        4600),
        (5100,  "Legend III",       4850),
        (5350,  "Legend II",        5100),
        (5600,  "Legend I",         5350),
        (6100,  "Mythic Grading",   5600),
        (6850,  "Mythic",           6100),
        (8600,  "Mythic Honor",     6850),
        (10600, "Mythic Glory",     8600),
        (float('inf'), "Mythic Immortal", 10600),
    ]
    for max_point, tier_name, min_point in tiers:
        if point <= max_point:
            star = (point - min_point) // 50
            return tier_name, star
    return "Mythic Immortal", (point - 10600) // 50
