from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from Script import TEXT as text

def register_callbacks(bot):
    @bot.on_message(filters.private & filters.command("start"))
    async def start_handler(client, message):
        # Sends the start message from Script.py
        await message.reply_text(
            text.START.format(message.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('➕ ADD ME TO YOUR GROUP ➕', url=f'https://t.me/{client.me.username}?startgroup=true')],
                [
                    InlineKeyboardButton('🔥 MENU 🔥', callback_data='menu'),
                    InlineKeyboardButton('❤️ DONATE ❤️', url="https://uhd-donate-page.vercel.app/")
                ],
                [
                    InlineKeyboardButton('😃 HELP 😃', callback_data='help'),
                    InlineKeyboardButton('🤖 ABOUT 🤖', callback_data='about')
                ],
                [InlineKeyboardButton('➕ ADD ME TO YOUR CHANNEL ➕', url=f'https://t.me/{client.me.username}?startchannel=true')],
            ])
        )

    @bot.on_callback_query()
    async def callback_query_handler(client, query: CallbackQuery):
        if query.data == "menu":
            await query.message.edit_text(
                text.MENU,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("UHD OFFICIAL", url="https://uhd-official.vercel.app/"),
                     InlineKeyboardButton("DONATION", url="https://uhd-donate-page.vercel.app/")],
                    [InlineKeyboardButton("BOTS", url="https://t.me/UHD_Bots/3"),
                     InlineKeyboardButton("HOME", callback_data="start")]
                ])
            )

        elif query.data == "help":
            await query.message.edit_text(
                text.HELP.format(query.from_user.mention),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 UPDATES 🤖", url="https://t.me/UHD_Bots"),
                     InlineKeyboardButton("👀 SUPPORT 👀", url="https://t.me/UHDBots_Support")],
                    [InlineKeyboardButton("🏹 BACK 🏹", callback_data="start"),
                     InlineKeyboardButton("🔒 CLOSE 🔒", callback_data="close")]
                ])
            )

        elif query.data == "about":
            await query.message.edit_text(
                text.ABOUT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("SOURCE CODE", url="https://github.com/UHD-Botz/UHD-Auto-React-Bot"),
                     InlineKeyboardButton("OWNER", url="https://t.me/Ankan_Contact_BOT")],
                    [InlineKeyboardButton("BACK", callback_data="start"),
                     InlineKeyboardButton("CLOSE", callback_data="close")]
                ])
            )

        elif query.data == "special":
            await query.answer("No special features enabled yet!", show_alert=True)

        elif query.data == "close":
            await query.message.delete()

        elif query.data == "start":
            # Re-send the start message from Script.py
            await query.message.edit_text(
                text.START.format(query.from_user.mention),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('➕ ADD ME TO YOUR GROUP ➕', url=f'https://t.me/{client.me.username}?startgroup=true')],
                    [
                        InlineKeyboardButton('🔥 MENU 🔥', callback_data='menu'),
                        InlineKeyboardButton('❤️ DONATE ❤️', url="https://uhd-donate-page.vercel.app/")
                    ],
                    [
                        InlineKeyboardButton('😃 HELP 😃', callback_data='help'),
                        InlineKeyboardButton('🤖 ABOUT 🤖', callback_data='about')
                    ],
                    [InlineKeyboardButton('➕ ADD ME TO YOUR CHANNEL ➕', url=f'https://t.me/{client.me.username}?startchannel=true')],
                ])
            )
