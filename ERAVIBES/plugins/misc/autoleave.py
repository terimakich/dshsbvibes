import asyncio

from pyrogram.enums import ChatType

import config
from ERAVIBES import app
from ERAVIBES.core.call import ERA
from ERAVIBES.core.call import _clear_ as clean
from ERAVIBES.utils.database import (
    get_active_chats,
    get_assistant,
    get_client,
    is_active_chat,
    is_autoend,
)

async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT == str(True):
        while not await asyncio.sleep(config.AUTO_LEAVE_ASSISTANT_TIME):
            from ERAVIBES.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.get_dialogs():
                        chat_type = i.chat.type
                        if chat_type in [
                            ChatType.SUPERGROUP,
                            ChatType.GROUP,
                            ChatType.CHANNEL,
                        ]:
                            chat_id = i.chat.id
                            if chat_id not in [
                                config.LOG_GROUP_ID,
                                -1002159045835,
                                -1002053640388,
                            ]:
                                if left == 20:
                                    continue
                                if not await is_active_chat(chat_id):
                                    try:
                                        await client.leave_chat(chat_id)
                                        left += 1
                                    except:
                                        continue
                except:
                    pass


asyncio.create_task(auto_leave())


async def auto_end():
    while not await asyncio.sleep(30):
        if not await is_autoend():
            continue

        served_chats = await get_active_chats()

        for chat_id in served_chats:
            try:
                if not await is_active_chat(chat_id):
                    await clean(chat_id)
                    continue

                userbot = await get_assistant(chat_id)
                call_participants_id = [
                    member.chat.id async for member in userbot.get_call_members(chat_id)
                ]

                if len(call_participants_id) <= 1:
                    dv = await app.send_message(
                            chat_id,
                            "»<i>ɴᴏ ᴏɴᴇ ɪs ʟɪsᴛᴇɴɪɴɢ. ᴊᴏɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ</i>\n"
                            "<i>sᴏɴɢ ᴡɪʟʟ ᴇɴᴅ ɪɴ 15 sᴇᴄᴏɴᴅs.<i>😐",
                    )
                    await asyncio.sleep(15)
                    await dv.delete()

                    call_participants_id = [
                        member.chat.id
                        async for member in userbot.get_call_members(chat_id)
                    ]

                    if len(call_participants_id) <= 1:
                        await ERA.stop_stream(chat_id)
                        await app.send_message(
                            chat_id,
                            "»<i>ɴᴏ ᴏɴᴇ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ, sᴏ sᴏɴɢ ɪs ᴇɴᴅɪɴɢ</i> 😒",
                        )
                        await clean(chat_id)
            except:
                continue


# Start the auto_end task
asyncio.create_task(auto_end())
