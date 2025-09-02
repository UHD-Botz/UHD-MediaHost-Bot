import os

class Config:
    # Telegram Bot Config
    API_ID = int(os.getenv("API_ID", ""))         # your API ID
    API_HASH = os.getenv("API_HASH", "")  # your API Hash
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # your Bot Token

    # Other Configs
    PORT = int(os.getenv("PORT", "8080"))
    ADMIN = int(os.getenv("ADMIN", ""))  # your telegram user id
