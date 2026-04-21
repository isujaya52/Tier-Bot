import BOT
from config import bot, LOGS_ID
import asyncio
from flask import Flask
from threading import Thread
import requests
import time
import os
from datetime import datetime

# 1. Tambahkan variabel global untuk mencatat waktu mulai
START_TIME = time.time()

flask_app = Flask(__name__)
main_loop = None

# Fungsi pembantu untuk mengubah detik menjadi format teks (Hari, Jam, Menit, Detik)
def get_readable_uptime():
    uptime_seconds = int(time.time() - START_TIME)
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)

@flask_app.route('/')
def flask_msg():
    # Menampilkan uptime di halaman web server juga
    return f"TIER BOT RUN | Uptime: {get_readable_uptime()}"

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000)

def keep_alive():
    google_url = "https://www.google.com/search?q=Google.com"
    own_url = f"https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')}/"
    
    while True:
        google_status = "❌"
        self_status = "❌"
        try:
            r1 = requests.get(google_url, timeout=10)
            google_status = f"✅ {r1.status_code}"
        except Exception as e:
            print(f"[keep-alive] google error: {e}")
            
        try:
            r2 = requests.get(own_url, timeout=10, verify=False)
            self_status = f"✅ {r2.status_code}"
        except Exception as e:
            print(f"[keep-alive] self error: {e}")

        try:
            if main_loop:
                # 2. Sisipkan Uptime ke dalam pesan log Telegram
                uptime_now = get_readable_uptime()
                msg = (
                    f"🟢 <b>BOT AKTIF</b>\n\n"
                    f"⏱️ <b>Uptime:</b> <code>{uptime_now}</code>\n"
                    f"🌐 Ping Google: {google_status}\n"
                    f"🖥️ Ping Self: {self_status}"
                )
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(LOGS_ID, msg, parse_mode='HTML'),
                    main_loop
                )
        except Exception as e:
            print(f"[keep-alive] log error: {e}")
        
        time.sleep(600)

async def runall():
    global main_loop
    main_loop = asyncio.get_event_loop()
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    # ... (sisanya tetap sama seperti kode Anda)
    try:
        from BOT.schedule import reset
        reset.start()
        print("Running PENJADWALAN SEASON")
    except Exception as e:
        print(e)

    while True:
        try:
            print(f"Bot starting... Uptime: {get_readable_uptime()}")
            await bot.infinity_polling(skip_pending=True, request_timeout=30)
        except Exception as e:
            print(f"Bot stopped with error: {e}")
        print("Bot offline. Restarting in 60 seconds...")
        await asyncio.sleep(60)

asyncio.run(runall())
