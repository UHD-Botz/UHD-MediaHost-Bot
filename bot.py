import os
import time
import asyncio
from pyrogram import Client, filters
from aiohttp import web
from config import Config
from utils import web_server
from db import Database

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
        self.db = Database(Config.DB_URI, Config.DB_NAME)

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.uptime = BOT_UPTIME

        # DB init
        await self.db.ensure_indexes()

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
            # ban check
            if await self.db.is_banned(message.from_user.id):
                return await message.reply_text("🚫 You are banned.")
            # save user
            await self.db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
            await self.db.log_event(type="start", user_id=message.from_user.id)
            await message.reply_text(
                "👋 Hello! I am UHD MediaToLink Bot.\n\nUse /ping to check latency or /uptime to see how long I’ve been running."
            )

        # -----------------
        # Stats (admin only)
        # -----------------
        @self.on_message(filters.command("stats") & filters.user(Config.ADMIN))
        async def stats(bot, message):
            total = await self.db.total_users()
            await message.reply_text(f"📊 Total users: {total}")

        # -----------------
        # Ban / Unban
        # -----------------
        @self.on_message(filters.command("ban") & filters.user(Config.ADMIN))
        async def ban_cmd(bot, message):
            args = message.command[1:]
            if not args:
                return await message.reply_text("Usage: /ban <user_id> [reason]")
            uid = int(args[0])
            reason = " ".join(args[1:]) if len(args) > 1 else None
            await self.db.ban(uid, reason, message.from_user.id)
            await message.reply_text(f"✅ Banned {uid}. Reason: {reason or '—'}")

        @self.on_message(filters.command("unban") & filters.user(Config.ADMIN))
        async def unban_cmd(bot, message):
            args = message.command[1:]
            if not args:
                return await message.reply_text("Usage: /unban <user_id>")
            uid = int(args[0])
            deleted = await self.db.unban(uid)
            if deleted:
                await message.reply_text(f"✅ Unbanned {uid}")
            else:
                await message.reply_text(f"ℹ️ {uid} was not banned")

        # -----------------
        # Catch-all private messages
        # -----------------
        @self.on_message(filters.private & ~filters.command(["start","ping","uptime","restart","stats","ban","unban"]))
        async def priv_handler(bot, message):
            if await self.db.is_banned(message.from_user.id):
                return await message.reply_text("🚫 You are banned.")
            await self.db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
            await self.db.log_event(type="msg", user_id=message.from_user.id, text=message.text or "", content=str(message.media))
            await message.reply_text("✅ Received your message.")

if __name__ == "__main__":
    UHDMediaToLinkBot().run()
