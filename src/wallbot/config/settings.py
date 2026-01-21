import os

TOKEN = os.getenv("BOT_TOKEN", "Bot Token does not exist")
PROFILE = os.getenv("PROFILE")

# Ensure SEARCH_INTERVAL is not less than 180 seconds
_search_interval = int(os.getenv("SEARCH_INTERVAL", "300"))
SEARCH_INTERVAL = max(_search_interval, 180)

# Cleanup settings (internal configuration)
CLEANUP_INTERVAL = 86400  # Run cleanup every 24 hours (in seconds)
CLEANUP_RETENTION_HOURS = 168  # Keep items for 7 days (in hours)

TELEGRAM_API_URL = "https://api.telegram.org/bot{}/".format(TOKEN)
WALLAPOP_API_URL = "https://api.wallapop.com/api/v3/search"

DATABASE_PATH = "db.sqlite" if PROFILE else "/data/db.sqlite"

LOG_LEVEL = "DEBUG" if PROFILE else "INFO"
LOG_PATH = "wallbot.log" if PROFILE else "/logs/wallbot.log"
