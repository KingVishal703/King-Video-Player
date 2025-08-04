import re
from os import environ

class Config:

# Bot Session Name
SESSION = environ.get('SESSION', 'TechVJBot')

# Your Telegram Account Api Id And Api Hash
API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

# Admin Telegram Account Id For Withdraw Notification Or Anything Else
ADMIN_ID = [int(i) for i in os.getenv("ADMIN_ID", "5654093580").split()]
# Back Up Bot Token For Fetching Message When Floodwait Comes
BACKUP_BOT_TOKEN = environ.get('BACKUP_BOT_TOKEN', "")

# Log Channel, In This Channel Your All File Stored.
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))

# Mongodb Database For User Link Click Count Etc Data Store.
MONGODB_URI = os.getenv("MONGODB_URI", "")
    DATABASE_NAME = "videobot"

# Stream Url Means Your Deploy Server App Url, Here You Media Will Be Stream And Ads Will Be Shown.
STREAM_URL = environ.get("STREAM_URL", "https://bottom-abbey-bjhchfguv-a18f9cc8.koyeb.app/")

# This Link Used As Permanent Link That If Your Deploy App Deleted Then You Change Stream Url, So This Link Will Redirect To Stream Url.
DOMAIN = os.getenv("DOMAIN", "https://short.domain")

SHORTENER_API = os.getenv("SHORTENER_API", "api_key_here")

# Others, Not Usefull
PORT = environ.get("PORT", "8080")
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
