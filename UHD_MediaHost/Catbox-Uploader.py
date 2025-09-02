from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__, filters
from pyrogram.raw.all import layer
import os, time, re, math
from catbox import CatboxUploader
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


RKN_PROGRESS = """<b>\n
╭━━━━❰RKN PROCESSING...❱━➣
┣⪼ 🗃️ ꜱɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ ᴅᴏɴᴇ : {0}%
┣⪼ 🚀 ꜱᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ ᴇᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:        
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["▣" for i in range(math.floor(percentage / 5))]),
            ''.join(["▢" for i in range(20 - math.floor(percentage / 5))])
        )            
        tmp = progress + RKN_PROGRESS.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),            
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(text=f"{ud_type}\n\n{tmp}")                         
        except:
            pass

def humanbytes(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2] 
    
async def catbox_link_convert(bot, update, edit):
    ext = ""
    if update.photo:
        ext = '.jpg'        
    elif update.video:
        ext = '.mp4'        
    elif update.document:
        ext = '.mkv'        
    elif update.audio:
        ext = '.mp3'
           
    medianame = "download/" + str(update.from_user.id) + ext
    dl_path = await bot.download_media(message=update, progress=progress_for_pyrogram,
            progress_args=('Uploading Catbox Server', edit, time.time()), file_name=medianame) if ext else await bot.download_media(message=update, progress=progress_for_pyrogram,
            progress_args=('Uploading Catbox Server', edit, time.time()))
    uploader = CatboxUploader()
    link = uploader.upload_file(dl_path)
    print(f'Uploaded file: {link}')
    try:
        os.remove(dl_path)
    except:
        pass
    return link

@Client.on_message(filters.command('start') & filters.private)
async def start_command(client, message):
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton('Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/RknDeveloper'),
        InlineKeyboardButton('Sᴜᴩᴩᴏʀᴛ', url='https://t.me/RknBots_Support')
        ],[
        #InlineKeyboardButton('🎛️ Aʙᴏᴜᴛ', callback_data='about'),
        #InlineKeyboardButton('🛠️ Hᴇʟᴩ', callback_data='help')
        #],[
        InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url="https://t.me/+klNh8N3hXjM1MDFk")
    ]])
    await message.reply_text("I Am Media To Link Convert Bot.", reply_markup=button)

async def file_size_function(update):
    try:
        file = getattr(update, update.media.value)
        if file.file_size > 200 * 1024 * 1024:
            return True
    except:
        return False
        
    return False
        
@Client.on_message(filters.media & filters.private)
async def getmedia(bot, update):
    if await file_size_function(update):
        return await update.reply_text("sᴏʀʀʏ ᴅᴜᴅᴇ, ᴛʜɪs ʙᴏᴛ ᴅᴏᴇsɴ'ᴛ sᴜᴘᴘᴏʀᴛ ғɪʟᴇs ʟᴀʀɢᴇʀ ᴛʜᴀɴ 200 ᴍʙ+")
       
    message = await update.reply_text(
            text="`Processing...`",
            quote=True,
            disable_web_page_preview=True
        )
    link = await catbox_link_convert(bot, update, message)
    reply_markup=InlineKeyboardMarkup(
        [[
        InlineKeyboardButton(text="Open Link", url=f"{link}"),
        InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={link}")
        ],[
        InlineKeyboardButton(text="Join Updates Channel", url="https://telegram.me/RknDeveloper")
        ]])   
    await message.edit_text(
        text=f"Link: `{link}`",
        disable_web_page_preview=False,
        reply_markup=reply_markup)
       
