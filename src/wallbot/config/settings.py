import os

TOKEN = os.getenv("BOT_TOKEN", "Bot Token does not exist")
PROFILE = os.getenv("PROFILE")
SEARCH_INTERVAL = int(os.getenv("SEARCH_INTERVAL", "300"))

TELEGRAM_API_URL = "https://api.telegram.org/bot{}/".format(TOKEN)
WALLAPOP_API_URL = "https://api.wallapop.com/api/v3/search"

DATABASE_PATH = "db.sqlite" if PROFILE else "/data/db.sqlite"

LOG_LEVEL = "DEBUG" if PROFILE else "INFO"
LOG_PATH = "wallbot.log" if PROFILE else "/logs/wallbot.log"
