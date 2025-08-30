# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys
import glob
import importlib.util
import logging
import logging.config
import pytz
import asyncio
from pathlib import Path
from datetime import date, datetime
from aiohttp import web
import Script
# Logging Setup
try:
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
except Exception as e:
    print(f"Logging configuration error: {e}")

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

from pyrogram import idle
from info import *
from Script import script
from plugins import web_server
from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# Plugin Loader
PLUGIN_PATH = Path("plugins")
plugin_files = glob.glob(str(PLUGIN_PATH / "*.py"))

# Start Bots
TechVJBot.start()
TechVJBackUpBot.start()

async def start():
    print('\n🔄 Initializing Your Bot...')

    # Start clients and get bot info
    try:
        bot_info = await TechVJBot.get_me()
        await initialize_clients()
    except Exception as e:
        logging.error(f"❌ Error initializing bot clients: {e}")
        sys.exit(1)

    # Load Plugins
    for file_path in plugin_files:
        plugin_name = Path(file_path).stem
        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[f"plugins.{plugin_name}"] = module
            print(f"✅ Plugin Loaded: {plugin_name}")
        except Exception as e:
            logging.warning(f"⚠️ Failed to load plugin {plugin_name}: {e}")

    # Heroku Ping Keepalive
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Restart Notification
    try:
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        await TechVJBot.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, time)
        )
    except Exception as e:
        logging.warning(f"⚠️ Failed to send restart log: {e}")

    # Web App Hosting
    try:
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        logging.info("🌐 Web server started successfully.")
    except Exception as e:
        logging.error(f"❌ Web server start failed: {e}")
        sys.exit(1)

    await idle()


if __name__ == '__main__':
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logging.info('🛑 Bot Stopped. Goodbye 👋')

