from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
import os

@Client.on_message(filters.media & filters.private)
async def upload_media(bot: Client, message: Message):
    m = await message.reply_text("📤 Uploading your file...")

    file_path = await message.download()
    
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename=os.path.basename(file_path))

                async with session.post("https://envs.sh", data=form) as resp:
                    link = await resp.text()

        await m.edit_text(f"✅ Uploaded Successfully!\n\n🔗 Link: `{link.strip()}`")

    except Exception as e:
        await m.edit_text(f"⚠️ Error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
