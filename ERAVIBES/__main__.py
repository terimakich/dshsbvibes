import asyncio
import importlib

from pyrogram import idle

import config
from config import BANNED_USERS
from ERAVIBES import HELPABLE, LOGGER, app, userbot
from ERAVIBES.core.call import ERA
from ERAVIBES.plugins import ALL_MODULES
from ERAVIBES.utils.database import get_banned_users, get_gbanned


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER("ERAVIBES").error(
            "No Assistant Clients Vars Defined!.. Exiting Process."
        )
        return
    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        LOGGER("ERAVIBES").warning(
            "No Spotify Vars defined. Your bot won't be able to play spotify queries."
        )

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()

    for all_module in ALL_MODULES:
        imported_module = importlib.import_module(all_module)

        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    LOGGER("ERAVIBES.plugins").info("𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗜𝗺𝗽𝗼𝗿𝘁𝗲𝗱 𝗔𝗹𝗹 𝗠𝗼𝗱𝘂𝗹𝗲𝘀 ✅")

    await userbot.start()
    await ERA.start()
    await ERA.decorators()
    LOGGER("ERAVIBES").info("🎉 𝗘𝗥𝗔𝗩𝗜𝗕𝗘𝗦🥳𝗦𝗧𝗔𝗥𝗧𝗘𝗗🥳𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 🎊")
    await idle()


if __name__ == "__main__":
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(init())
    LOGGER("ERAVIBES").info("𝗦𝘁𝗼𝗽𝗽𝗶𝗻𝗴 𝗘𝗥𝗔𝗩𝗜𝗕𝗘𝗦! 𝗚𝗼𝗼𝗱𝗕𝘆𝗲 🥹")
