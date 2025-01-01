from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from ERAVIBES import app
from ERAVIBES.core.call import ERA 
from ERAVIBES.utils import bot_sys_stats
from ERAVIBES.utils.inline import supp_markup
from config import BANNED_USERS, D
from strings import get_string


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
async def ping(client, message: Message):
    try:
        # React with random emoji
        await message.react(random.choice(D))
    except Exception as e:
        print(f"Reaction Error: {e}")

    start = datetime.now()
    response = await message.reply_photo(
        caption=get_string()["ping_1"].format(app.mention),  # Fixed here
    )
    pytgping = await ERA.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        get_string()["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),  # Fixed here
        reply_markup=supp_markup(),
    )
