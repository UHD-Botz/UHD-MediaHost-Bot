from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, InputUserDeactivated
import asyncio
from config import ADMIN

# In-memory storage for users
USERS = set()

# Parse inline buttons in broadcast messages
def parse_button_markup(text: str):
    lines = text.split("\n")
    buttons = []
    final_text_lines = []
    for line in lines:
        row = []
        parts = line.split("||")
        is_button_line = True
        for part in parts:
            import re
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


@Client.on_message(filters.private & filters.command("start"))
async def register_user(client: Client, message: Message):
    USERS.add(message.from_user.id)
    await message.reply_text("✅ You are registered to receive broadcasts.")


@Client.on_message(filters.private & filters.command("broadcast") & filters.user(ADMIN))
async def broadcasting_func(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message to broadcast.")

    msg = await message.reply_text("⏳ Processing broadcast...")
    to_copy_msg = message.reply_to_message
    users_list = list(USERS)
    completed = 0
    failed = 0

    raw_text = to_copy_msg.caption or to_copy_msg.text or ""
    reply_markup, cleaned_text = parse_button_markup(raw_text)

    for i, user_id in enumerate(users_list):
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
            USERS.discard(user_id)
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

        await msg.edit(f"Total: {i+1}\nCompleted: {completed}\nFailed: {failed}")
        await asyncio.sleep(0.1)

    await msg.edit(
        f"📣 Broadcast Completed\n\nTotal Users: {len(users_list)}\n✅ Successful: {completed}\n❌ Failed: {failed}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎭 Close", callback_data="close")]])
    )
