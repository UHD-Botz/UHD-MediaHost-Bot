from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates Channel", url="https://t.me/RknDeveloper")],
        [InlineKeyboardButton("Support Group", url="https://t.me/RknBots_Support")]
    ])
    await message.reply_text(
        "👋 Hello!\nI am UHD Media Host Bot.\nSend me a photo/video/document and I will upload it to envs.sh and give you the link.",
        reply_markup=button
    )
