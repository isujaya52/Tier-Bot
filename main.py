import BOT
from config import bot, LOGS_ID
import asyncio
from flask import Flask
from threading import Thread
import requests
import time
import os
from datetime import datetime
from BOT.all_cmd import ping, get_readable_uptime

flask_app = Flask(__name__)

# Variabel global untuk menyimpan loop utama
main_loop = None

@flask_app.route('/')
def flask_msg():
    return f"TIER BOT RUN | Uptime: {get_readable_uptime()}"

def run_flask():
    # Gunakan threaded=True agar flask tidak memblokir thread utamanya sendiri
    flask_app.run(host="0.0.0.0", port=5000, threaded=True)

def keep_alive_worker():
    """
    Fungsi ini berjalan di thread terpisah.
    Ia bertugas memerintahkan loop utama untuk menjalankan fungsi ping.
    """
    while True:
        try:
            # Pastikan loop sudah berjalan
            if maim_loop:
                # Ambil coroutine ping
                coro = ping() 
                
                
                # Kirim pesan hasil ping ke Telegram lewat loop utama
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(LOGS_ID, msg, parse_mode='HTML'),
                    loop
                )
        except Exception as e:
            print(f"[keep-alive] loop error: {e}")
        
        time.sleep(600) # Tunggu 10 menit

async def runall():
    global main_loop
    # 1. Dapatkan loop yang sedang berjalan saat ini
    main_loop = asyncio.get_running_loop()

    # 2. Jalankan Flask di Thread terpisah
    Thread(target=run_flask, daemon=True).start()

    # 3. Jalankan Worker Keep Alive di Thread terpisah, kirim main_loop sebagai argumen
    Thread(target=keep_alive_worker, args=(main_loop,), daemon=True).start()
    
    # 4. Inisialisasi Penjadwalan
    try:
        from BOT.schedule import reset
        reset.start()
        print("Running PENJADWALAN SEASON")
    except Exception as e:
        print(f"Schedule Error: {e}")

    # 5. Main Loop Bot (Infinity Polling)
    while True:
        try:
            print(f"Bot starting... Uptime: {get_readable_uptime()}")
            # Gunakan await karena kita berada di dalam fungsi async
            await bot.infinity_polling(skip_pending=True, request_timeout=30)
        except Exception as e:
            print(f"Bot stopped with error: {e}")
        
        print("Bot offline. Restarting in 60 seconds...")
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(runall())
    except KeyboardInterrupt:
        print("Bot dimatikan secara manual.")
