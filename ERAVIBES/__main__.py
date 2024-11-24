import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ERAVIBES import LOGGER, app, userbot
from ERAVIBES.core.call import Tanu
from ERAVIBES.misc import sudo
from ERAVIBES.plugins import ALL_MODULES
from ERAVIBES.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("✦ Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ERAVIBES.plugins" + all_module)
    LOGGER("ERAVIBES.plugins").info("✦ Successfully Imported Modules...💞")
    await userbot.start()
    await Tanu.start()
    try:
        await Tanu.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ERAVIBES").error(
            "✦ Please turn on the videochat of your log group\channel.\n\n✦ Stopping Bot...💣"
        )
        exit()
    except:
        pass
    await Tanu.decorators()
    LOGGER("ERAVIBES").info(
        "✦ Created By ➥ The Dvis...🐝"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("ERAVIBES").info("❖ Stopping Tanu Music Bot...💌")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
