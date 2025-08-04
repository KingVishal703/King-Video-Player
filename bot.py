# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path

# Logging Setup
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import idle 
from info import *
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server

from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# Plugin Loader
ppath = "plugins/*.py"
files = glob.glob(ppath)

# Start Bots
TechVJBot.start()
TechVJBackUpBot.start()

loop = asyncio.get_event_loop()

async def start():
    print('\n🔄 Initializing Your Bot...')
    try:
        bot_info = await TechVJBot.get_me()
        await initialize_clients()
    except Exception as e:
        logging.error(f"❌ Error initializing bot clients: {e}")
        sys.exit(1)

    # Load Plugins
    for name in files:
        try:
            with open(name) as a:
                patt = Path(a.name)
                plugin_name = patt.stem.replace(".py", "")
                plugins_dir = Path(f"plugins/{plugin_name}.py")
                import_path = "plugins.{}".format(plugin_name)
                spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules["plugins." + plugin_name] = load
                print(f"✅ Plugin Loaded: {plugin_name}")
        except Exception as e:
            logging.warning(f"⚠️ Failed to load plugin {name}: {e}")

    # Keepalive for Heroku
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

    # Web App for Stream
    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        logging.info("🌐 Web server started successfully.")
    except Exception as e:
        logging.error(f"❌ Web server start failed: {e}")
        sys.exit(1)

    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('🛑 Bot Stopped. Goodbye 👋')
