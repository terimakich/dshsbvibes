import asyncio
from pyrogram import filters
from pyrogram.types import Message

from ERAVIBES import app
from ERAVIBES.core.call import ERA
from ERAVIBES.utils.database import set_loop



@app.on_message(filters.video_chat_started & filters.group)
async def brah(_, msg):
    chat_id = msg.chat.id
    try:
        await msg.reply("<b>😍ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ🥳</b>")
        await ERA.stop_stream(chat_id)
        await set_loop(chat_id, 0)
    except Exception as e:
        return await msg.reply(f"<b>Error {e}</b>")


# vc off
@app.on_message(filters.video_chat_ended & filters.group)
async def brah2(_, msg):
    chat_id = msg.chat.id
    try:
        await msg.reply("<b>😕ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ💔</b>")
        await ERA.stop_stream(chat_id)
        await set_loop(chat_id, 0)
    except Exception as e:
        return await msg.reply(f"<b>Error {e}</b>")
