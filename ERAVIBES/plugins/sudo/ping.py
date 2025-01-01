from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from ERAVIBES import app
from ERAVIBES.core.call import ERA 
from ERAVIBES.utils import bot_sys_stats
from ERAVIBES.utils.inline import supp_markup
from ERAVIBES.utils.decorators.language import language
from ERAVIBES.utils.database import get_lang
from config import BANNED_USERS, D
from strings import get_string

@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping(client, message: Message, lang):
    try:
        lang_code = lang.get("language_code", "en")  # Extract language code
        await message.react(random.choice(D))
    except Exception as e:
        print(f"Reaction Error: {e}")

    start = datetime.now()
    response = await message.reply_text(
        text=get_string(lang_code)["ping_1"].format(app.mention),
    )
    pytgping = await ERA.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        text=get_string(lang_code)["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(),
    )
