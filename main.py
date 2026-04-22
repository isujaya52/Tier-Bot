import BOT
from config import bot, LOGS_ID
import asyncio
from flask import Flask
from threading import Thread
import requests
import time
import os
from datetime import datetime
from BOT.all_cmd import ping
from BOT.all_cmd import get_readable_uptime


flask_app = Flask(__name__)
main_loop = None

@flask_app.route('/')
def flask_msg():
    # Menampilkan uptime di halaman web server juga
    return f"TIER BOT RUN | Uptime: {get_readable_uptime()}"

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000)

def keep_alive():
    while True:
        try:
            # Karena ini di dalam thread, kita gunakan run_coroutine_threadsafe
            if main_loop:
                # Ambil pesan dari fungsi check_status
                piing = ping()
                msg = asyncio.run_coroutine_threadsafe(piing, main_loop).result()
                
                # Kirim ke LOGS_ID
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(LOGS_ID, msg, parse_mode='HTML'),
                    main_loop
                )
        except Exception as e:
            print(f"[keep-alive] loop error: {e}")
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
