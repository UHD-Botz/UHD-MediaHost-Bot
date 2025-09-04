import os
import time
import asyncio
from pyrogram import Client, filters
from aiohttp import web
from config import Config
from utils import web_server

BOT_UPTIME = time.time()

class UHDMediaToLinkBot(Client):
    def __init__(self):
        super().__init__(
            name="UHDMediaToLinkBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.uptime = BOT_UPTIME

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", getattr(Config, "PORT", 8080)).start()

        print(f"{me.first_name} Started.....✨️")

        # Notify admin that bot is online
        if getattr(Config, "ADMIN", None):
            try:
                await self.send_message(Config.ADMIN[0], "✅ Bot restarted and is now online!")
            except:
                pass

        self.add_handlers()

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")

    def add_handlers(self):
        # -----------------
        # Ping
        # -----------------
        @self.on_message(filters.command("ping"))
        async def ping(bot, message):
            start = time.time()
            msg = await message.reply_text("🏓 Pinging...")
            end = time.time()
            await msg.edit_text(f"🏓 Pong!\nResponse time: {round((end-start)*1000)} ms")

        # -----------------
        # Uptime
        # -----------------
        @self.on_message(filters.command("uptime"))
        async def uptime(bot, message):
            uptime_seconds = int(time.time() - BOT_UPTIME)
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await message.reply_text(f"⏱ Bot Uptime: {hours}h {minutes}m {seconds}s")

        # -----------------
        # Restart (admin only)
        # -----------------
        @self.on_message(filters.command("restart") & filters.user(Config.ADMIN))
        async def restart_handler(bot, message):
            await message.reply_text("♻️ Restarting bot...")
            async def restart_later():
                await asyncio.sleep(1)
                os._exit(0)
            asyncio.create_task(restart_later())

        # -----------------
        # Start
        # -----------------
        @self.on_message(filters.private & filters.command("start"))
        async def start_cmd(bot, message):
            await message.reply_text(
                "👋 Hello! I am UHD MediaToLink Bot.\n\n"
                "Use /ping to check latency or /uptime to see how long I’ve been running."
            )

if __name__ == "__main__":
    UHDMediaToLinkBot().run()
