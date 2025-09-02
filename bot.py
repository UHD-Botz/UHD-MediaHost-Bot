from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters
from aiohttp import web
from utils import web_server
import time
from config import Config
import os

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

        # Notify admin only
        if getattr(Config, "ADMIN", None):
            try:
                await self.send_message(Config.ADMIN, f"**__{me.first_name} Started.....✨️__**")
            except:
                pass

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")


# -----------------------------
# Ping Feature
# -----------------------------
@UHDMediaToLinkBot.on_message(filters.command("ping"))
async def ping(bot, message):
    start_time = time.time()
    msg = await message.reply_text("🏓 Pinging...")
    end_time = time.time()
    await msg.edit_text(f"🏓 Pong!\nResponse time: {round((end_time - start_time)*1000)} ms")


# -----------------------------
# Stats Feature
# -----------------------------
@UHDMediaToLinkBot.on_message(filters.command("stats"))
async def stats(bot, message):
    uptime_seconds = int(time.time() - BOT_UPTIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    text = (
        f"📊 **Bot Statistics**\n"
        f"• Uptime: `{uptime}`\n"
        f"• Bot Name: `{bot.username}`\n"
        f"• Admin: `{Config.ADMIN}`"
    )
    await message.reply_text(text)


# -----------------------------
# Emoji / Reaction Feature
# -----------------------------
@UHDMediaToLinkBot.on_message(filters.text)
async def react_with_emoji(bot, message):
    # Ignore commands
    if message.text.startswith("/"):
        return
    try:
        # Simple reaction: reply with 👍 emoji to every text message
        await message.reply_text("👍")
    except Exception:
        pass


if __name__ == "__main__":
    UHDMediaToLinkBot().run()
