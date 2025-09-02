from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import upload_to_envs
import os, time

@Client.on_message(filters.media & filters.private)
async def media_handler(bot, update):
    # file size check
    try:
        file = getattr(update, update.media.value)
        if file.file_size and file.file_size > 200*1024*1024:
            return await update.reply_text("❌ File too large! Max 200MB.")
    except:
        pass

    message = await update.reply_text("⏳ Processing...", quote=True, disable_web_page_preview=True)

    ext = ""
    if update.photo: ext = ".jpg"
    elif update.video: ext = ".mp4"
    elif update.document: ext = os.path.splitext(update.document.file_name)[1] or ".bin"
    elif update.audio: ext = ".mp3"

    ts = int(time.time())
    filename = f"{update.from_user.id}_{ts}{ext}"
    dl_dir = "download"
    if not os.path.exists(dl_dir):
        os.makedirs(dl_dir, exist_ok=True)

    dl_path = await bot.download_media(
        message=update,
        progress=None,
        file_name=os.path.join(dl_dir, filename)
    )

    try:
        link = await upload_to_envs(dl_path)
    except Exception as e:
        await message.edit_text(f"❌ Upload failed: {e}")
        if os.path.exists(dl_path): os.remove(dl_path)
        return

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Link", url=f"{link}"),
         InlineKeyboardButton("Share Link", url=f"https://telegram.me/share/url?url={link}")],
        [InlineKeyboardButton("Updates Channel", url="https://t.me/RknDeveloper")]
    ])
    await message.edit_text(text=f"🔗 Link: `{link}`", disable_web_page_preview=False, reply_markup=reply_markup)
    if os.path.exists(dl_path): os.remove(dl_path)
