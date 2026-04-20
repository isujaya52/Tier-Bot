import BOT
from config import bot, LOGS_ID
import asyncio
from flask import Flask
from threading import Thread
import requests
import time
import os


flask_app = Flask(__name__)
main_loop = None


@flask_app.route('/')
def flask_msg():
    return "TIER BOT RUN"


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
            print(f"[keep-alive] ping google -> {r1.status_code}")
        except Exception as e:
            print(f"[keep-alive] google error: {e}")
        try:
            r2 = requests.get(own_url, timeout=10, verify=False)
            self_status = f"✅ {r2.status_code}"
            print(f"[keep-alive] ping self -> {r2.status_code}")
        except Exception as e:
            print(f"[keep-alive] self error: {e}")
        try:
            if main_loop:
                msg = (
                    f"🟢 <b>BOT AKTIF</b>\n\n"
                    f"🌐 Ping Google: {google_status}\n"
                    f"🖥️ Ping Self: {self_status}"
                )
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(LOGS_ID, msg),
                    main_loop
                )
        except Exception as e:
            print(f"[keep-alive] log error: {e}")
        time.sleep(240)


async def runall():
    global main_loop
    main_loop = asyncio.get_event_loop()
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    try:
        from BOT.schedule import reset
        reset.start()
        for job in reset.get_jobs():
            print(job)
        print("Running PENJADWALAN SEASON")
    except Exception as e:
        print(e)

    while True:
        try:
            print("Bot starting...")
            await bot.infinity_polling(skip_pending=True, request_timeout=30)
        except Exception as e:
            print(f"Bot stopped with error: {e}")
        print("Bot offline. Restarting in 60 seconds...")
        await asyncio.sleep(60)


asyncio.run(runall())
