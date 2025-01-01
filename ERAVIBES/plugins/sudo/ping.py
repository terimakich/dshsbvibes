from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from ERAVIBES import app
from ERAVIBES.core.call import ERA
from ERAVIBES.utils import bot_sys_stats
from ERAVIBES.utils.decorators.language import language
from ERAVIBES.utils.inline import support_group_markup


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    response = await message.reply_text(
        text=_["ping_1"].format(app.mention),
    )
    start = datetime.now()
    pytgping = await ERA.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(
            resp,
            app.mention,
            UP,
            RAM,
            CPU,
            DISK,
            pytgping,
        ),
       # reply_markup=support_group_markup(_),
    )
