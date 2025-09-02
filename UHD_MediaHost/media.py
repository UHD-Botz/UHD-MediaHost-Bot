from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import upload_to_envs
import os, time
import pyrogram.errors

# Helper function to safely edit messages
async def safe_edit(message, new_text, reply_markup=None):
    if message.text != new_text:
        try:
            await message.edit_text(text=new_text, disable_web_page_preview=False, reply_markup=reply_markup)
        except pyrogram.errors.MessageNotModified:
            pass

@Client.on_message(filters.media & filters.private)
async def media_handler(bot, update):
    # File size check
    try:
        file = getattr(update, update.media.value)
        if file.file_size and file.file_size > 200*1024*1024:
            return await update.reply_text("❌ File too large! Max 200MB.")
    except:
        pass

    message = await update.reply_text("⏳ Processing... 0%", quote=True, disable_web_page_preview=True)

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

    # Download with progress updates
    async def download_progress(current, total):
        percent = int(current * 100 / total)
        if percent in [25, 50, 75]:
            await safe_edit(message, f"⏳ Processing... {percent}%")

    dl_path = await bot.download_media(
        message=update,
        progress=download_progress,
        file_name=os.path.join(dl_dir, filename)
    )

    try:
        link = await upload_to_envs(dl_path)
    except Exception as e:
        await safe_edit(message, f"❌ Upload failed: {e}")
        if os.path.exists(dl_path): os.remove(dl_path)
        return

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Link", url=f"{link}"),
         InlineKeyboardButton("Share Link", url=f"https://telegram.me/share/url?url={link}")],
        [InlineKeyboardButton("Updates Channel", url="https://t.me/RknDeveloper")]
    ])

    # Final message with the link
    await safe_edit(message, f"🔗 Link: `{link}`", reply_markup=reply_markup)

    # Clean up downloaded file
    if os.path.exists(dl_path): os.remove(dl_path)
