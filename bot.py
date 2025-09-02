from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__, filters
from pyrogram.raw.all import layer
from aiohttp import web
from utils import web_server
import time
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config

# other configs
BOT_UPTIME = time.time()

class UHDMediaToLinkBot(Client):
    def __init__(self):
        super().__init__(
            name="UHDMediaToLinkBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={"root": "UHDMediaToLinkBot"},
            workers=200,
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = BOT_UPTIME
        
        app = web.AppRunner(await web_server())
        await app.setup()       
        await web.TCPSite(app, "0.0.0.0", Config.PORT).start()
            
        print(f"{me.first_name} Started.....✨️")
        if Config.ADMIN:
            try:
                await self.send_message(Config.ADMIN, f"**__{me.first_name} Started.....✨️__**")                                
            except:
                pass
                
    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")

            
UHDMediaToLinkBot().run()
