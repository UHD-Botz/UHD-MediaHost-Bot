from datetime import datetime
from pytz import timezone
from pyrogram import Client
from aiohttp import web
from utils import web_server
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

        # Notify admin only
        if getattr(Config, "ADMIN", None):
            try:
                await self.send_message(Config.ADMIN, f"**__{me.first_name} Started.....✨️__**")
            except:
                pass

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")


if __name__ == "__main__":
    UHDMediaToLinkBot().run()
