import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiohttp import web
from config import Config
from utils import web_server

BOT_UPTIME = time.time()

# -----------------------------
# Texts
# -----------------------------
class TEXT:
    START = """<b>{},

ɪ ᴀᴍ ʟᴀᴛᴇsᴛ ɢᴇɴᴇʀᴀᴛɪᴏɴ ᴘᴏᴡᴇʀꜰᴜʟʟ ᴀᴜᴛᴏ ʀᴇᴀᴄᴛɪᴏɴ ʙᴏᴛ.

ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴀs ᴀ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ ᴛʜᴇɴ sᴇᴇ ᴍʏ ᴘᴏᴡᴇʀ.

<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://telegram.me/Ankan_Contact_Bot'>ᴀɴᴋᴀɴ</a></blockquote></b>"""

    ABOUT = """<b>📜 Cʜᴇᴄᴋ Aʙᴏᴜᴛ:
  
📚 Lɪʙʀᴀʀʏ: Pʏʀᴏɢʀᴀᴍ  
🧑‍💻 Lᴀɴɢᴜᴀɢᴇ: Pʏᴛʜᴏɴ  
🌐 Sᴇʀᴠᴇʀ: ᴋᴏʏᴇʙ  
🚀 ᴠᴇʀsɪᴏɴ: V2.0  
👇 Sᴏᴜʀᴄᴇ Cᴏᴅᴇ: (ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ) 

<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://telegram.me/Ankan_Contact_Bot'>ᴀɴᴋᴀɴ</a></blockquote></b>"""

    HELP = """<b>{},

ᴛʜɪꜱ ɪꜱ ʀᴇᴀʟʟʏ sɪᴍᴘʟᴇ 🤣  

ᴊᴜsᴛ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴏʀ ᴄʜᴀɴɴᴇʟ, ᴀɴᴅ ᴇɴᴊᴏʏ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴍᴀɢɪᴄᴀʟ ʀᴇᴀᴄᴛɪᴏɴs 💞

<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://telegram.me/Ankan_Contact_Bot'>ᴀɴᴋᴀɴ</a></blockquote></b>"""

    MENU = """
🔥 **ʜᴇʀᴇ ɪꜱ ᴀʟʟ ɪᴍᴘᴏʀᴛᴀɴᴛ ʙᴜᴛᴛᴏɴs ᴄʜᴇᴄᴋ ɪᴛ ᴏᴜᴛ** 🔥"""

# -----------------------------
# Bot Class
# -----------------------------
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
        self.me = me
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
        @self.on_message(filters.command("start") & filters.private)
        async def start_handler(bot, message):
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f'https://t.me/{bot.me.username}?startgroup=true')],
                [
                    InlineKeyboardButton('🔥 ᴍᴇɴᴜ 🔥', callback_data='menu'),
                    InlineKeyboardButton('❤️ ᴅᴏɴᴀᴛᴇ ❤️', url="https://uhd-donate-page.vercel.app/")
                ],
                [
                    InlineKeyboardButton('😃 ʜᴇʟᴘ 😃', callback_data='help'),
                    InlineKeyboardButton('🤖 ᴀʙᴏᴜᴛ 🤖', callback_data='about')
                ],
                [InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ➕', url=f'https://t.me/{bot.me.username}?startchannel=true')],
            ])

            await message.reply_text(
                TEXT.START.format(message.from_user.mention),
                disable_web_page_preview=True,
                reply_markup=buttons
            )

        # -----------------
        # Callback Handler
        # -----------------
        @self.on_callback_query()
        async def callbacks(bot, query: CallbackQuery):
            if query.data == "about":
                await query.message.edit_text(TEXT.ABOUT, disable_web_page_preview=True)
            elif query.data == "help":
                await query.message.edit_text(TEXT.HELP.format(query.from_user.first_name), disable_web_page_preview=True)
            elif query.data == "menu":
                await query.message.edit_text(TEXT.MENU, disable_web_page_preview=True)


if __name__ == "__main__":
    UHDMediaToLinkBot().run()
