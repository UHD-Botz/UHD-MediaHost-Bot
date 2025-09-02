from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters
from aiohttp import web
from utils import web_server, send_log_message, upload_to_envs
import time
from config import Config

BOT_UPTIME = time.time()


class UHDMediaToLinkBot(Client):
    def __init__(self):
        super().__init__(
            name="UHDMediaToLinkBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={"root": "UHD_MediaHost"},
            workers=200,
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = BOT_UPTIME
        
        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", getattr(Config, "PORT", 8080)).start()
            
        print(f"{me.first_name} Started.....✨️")

        # Log to admin
        if getattr(Config, "ADMIN", None):
            try:
                await self.send_message(Config.ADMIN, f"**__{me.first_name} Started.....✨️__**")
            except:
                pass

        # Log to LOG_CHANNEL
        await send_log_message(self, f"**__{me.first_name} Bot Started at {datetime.now()} ✨️__**")

    async def stop(self, *args):
        await send_log_message(self, f"**__Bot Stopped at {datetime.now()} 🙄__**")
        await super().stop()
        print("Bot Stopped 🙄")


# -----------------------------
# Command Logging
# -----------------------------
@UHDMediaToLinkBot.on_message(filters.command)
async def log_commands(bot, message):
    user = message.from_user
    if user:
        text = f"User @{user.username or 'Unknown'} (ID: {user.id}) used command: {message.text}"
        await send_log_message(bot, text)


# -----------------------------
# Example: File Upload Logging
# -----------------------------
async def handle_file_upload(bot, message, file_path):
    user = message.from_user
    size_mb = round(os.path.getsize(file_path)/1024/1024, 2)
    filename = os.path.basename(file_path)

    # Log file upload
    text = f"User @{user.username or 'Unknown'} (ID: {user.id}) uploaded: {filename} ({size_mb} MB)"
    await send_log_message(bot, text)

    # Upload file to envs.sh
    try:
        link = await upload_to_envs(file_path)
        return link
    except Exception as e:
        await send_log_message(bot, f"Error uploading {filename} by @{user.username or 'Unknown'}: {e}")
        raise e


if __name__ == "__main__":
    UHDMediaToLinkBot().run()
