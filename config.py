import os

class Config:
    # Telegram Bot Config
    API_ID = int(os.getenv("API_ID", "23889992"))         # your API ID
    API_HASH = os.getenv("API_HASH", "70bf3c9baebf30afff8c32649bf23c3d")  # your API Hash
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # your Bot Token
    DB_URI = os.environ.get("DB_URI", "")         
    DB_NAME = os.environ.get("DB_NAME", "")

    # Other Configs
    PORT = int(os.getenv("PORT", "8080"))
    ADMIN = int(os.getenv("ADMIN", ""))  # your telegram user id
