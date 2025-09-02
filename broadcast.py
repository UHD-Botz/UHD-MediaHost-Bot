from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, InputUserDeactivated
import asyncio
from config import ADMIN
from db import get_all_users, remove_user

# ------------------------
# Parse buttons from text
# ------------------------
def parse_button_markup(text: str):
    import re
    lines = text.split("\n")
    buttons = []
    final_text_lines = []

    for line in lines:
        row = []
        parts = line.split("||")
        is_button_line = True
        for part in parts:
            match = re.fullmatch(r"\[(.+?)\]\((https?://[^\s]+)\)", part.strip())
            if match:
                row.append(InlineKeyboardButton(match[1], url=match[2]))
            else:
                is_button_line = False
                break
        if is_button_line and row:
            buttons.append(row)
        else:
            final_text_lines.append(line)
    return InlineKeyboardMarkup(buttons) if buttons else None, "\n".join(final_text_lines).strip()


# ------------------------
# Register users
# ------------------------
@Client.on_message(filters.private & filters.command("start"))
async def register_user(client: Client, message: Message):
    from db import add_user
    await add_user(message.from_user.id)
    await message.reply("✅ You are registered to receive broadcasts.")


# ------------------------
# Broadcast command
# ------------------------
@Client.on_message(filters.private & filters.command("broadcast") & filters.user(ADMIN))
async def broadcasting_func(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to a message to broadcast.")

    msg = await message.reply("⏳ Processing broadcast...")
    to_copy_msg = message.reply_to_message
    users_list = await get_all_users()
    completed = 0
    failed = 0

    raw_text = to_copy_msg.caption or to_copy_msg.text or ""
    reply_markup, cleaned_text = parse_button_markup(raw_text)

    tasks = []
    for i, user_id in enumerate(users_list):
        async def send_msg(user_id=user_id):
            nonlocal completed, failed
            try:
                if to_copy_msg.text:
                    await client.send_message(user_id, cleaned_text, reply_markup=reply_markup)
                elif to_copy_msg.photo:
                    await client.send_photo(user_id, to_copy_msg.photo.file_id, caption=cleaned_text, reply_markup=reply_markup)
                elif to_copy_msg.video:
                    await client.send_video(user_id, to_copy_msg.video.file_id, caption=cleaned_text, reply_markup=reply_markup)
                elif to_copy_msg.document:
                    await client.send_document(user_id, to_copy_msg.document.file_id, caption=cleaned_text, reply_markup=reply_markup)
                else:
                    await to_copy_msg.copy(user_id)
                completed += 1
            except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated):
                await remove_user(user_id)
                failed += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await to_copy_msg.copy(user_id)
                    completed += 1
                except:
                    failed += 1
            except Exception as e:
                print(f"Broadcast to {user_id} failed: {e}")
                failed += 1
            await msg.edit(f"Total: {i+1}\n✅ Done: {completed}\n❌ Failed: {failed}")

        tasks.append(asyncio.create_task(send_msg()))
        await asyncio.sleep(0.05)  # small throttle

    await asyncio.gather(*tasks)
    await msg.edit(f"📣 Broadcast Completed\nTotal Users: {len(users_list)}\n✅ Done: {completed}\n❌ Failed: {failed}")
