import os
import time
import asyncio
from pyrogram import Client, filters
from aiohttp import web
from config import Config
from broadcast import USERS  # import USERS for broadcast memory
from broadcast import broadcasting_func  # register broadcast handler
from utils import web_server

BOT_UPTIME = time.time()
BANNED_USERS = set()  # In-memory banned users

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
        self.username = me.username
        self.uptime = BOT_UPTIME

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", Config.PORT).start()

        print(f"{me.first_name} Started.....✨️")

        # Notify admin
        if getattr(Config, "ADMIN", None):
            try:
                await self.send_message(Config.ADMIN[0], "✅ Bot restarted and is now online!")
            except:
                pass

        # Register handlers
        self.add_handlers()

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")

    def add_handlers(self):
        # Ping
        @self.on_message(filters.command("ping"))
        async def ping(bot, message):
            start = time.time()
            msg = await message.reply_text("🏓 Pinging...")
            end = time.time()
            await msg.edit_text(f"🏓 Pong!\nResponse time: {round((end-start)*1000)} ms")

        # Uptime
        @self.on_message(filters.command("uptime"))
        async def uptime(bot, message):
            uptime_seconds = int(time.time() - BOT_UPTIME)
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await message.reply_text(f"⏱ Bot Uptime: {hours}h {minutes}m {seconds}s")

        # Restart
        @self.on_message(filters.command("restart") & filters.user(Config.ADMIN))
        async def restart_handler(bot, message):
            await message.reply_text("♻️ Restarting bot...")
            async def restart_later():
                await asyncio.sleep(1)
                os._exit(0)
            asyncio.create_task(restart_later())

        # Ban
        @self.on_message(filters.command("ban") & filters.user(Config.ADMIN))
        async def ban_user(bot, message):
            if not message.reply_to_message:
                await message.reply_text("⚠️ Reply to the user to ban.")
                return
            user_id = message.reply_to_message.from_user.id
            if user_id in BANNED_USERS:
                await message.reply_text("User is already banned.")
                return
            BANNED_USERS.add(user_id)
            await message.reply_text(f"✅ User {user_id} banned.")

        # Unban
        @self.on_message(filters.command("unban") & filters.user(Config.ADMIN))
        async def unban_user(bot, message):
            if not message.reply_to_message:
                await message.reply_text("⚠️ Reply to the banned user to unban.")
                return
            user_id = message.reply_to_message.from_user.id
            if user_id not in BANNED_USERS:
                await message.reply_text("User is not banned.")
                return
            BANNED_USERS.remove(user_id)
            await message.reply_text(f"✅ User {user_id} unbanned.")

        # Block banned users
        @self.on_message(filters.incoming)
        async def block_banned(bot, message):
            if message.from_user and message.from_user.id in BANNED_USERS:
                try:
                    await message.delete()
                except:
                    pass
                return  # stop processing


if __name__ == "__main__":
    UHDMediaToLinkBot().run()
