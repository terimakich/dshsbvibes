import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

from ERAVIBES.core.call import ERA
from ERAVIBES.core.userbot import Userbot
from ERAVIBES.utils.database import get_assistant
from ERAVIBES import app


photo = [
    "https://envs.sh/qeq.jpg",
    "https://envs.sh/qe0.jpg",
    "https://envs.sh/qeS.jpg",
    "https://envs.sh/qeW.jpg",
]


@app.on_chat_member_updated(filters.group, group=6)
async def assistant_banned(client: app, member: ChatMemberUpdated):
    chat_id = member.chat.id
    userbot = await get_assistant(chat_id)
    try:
        userbot = await get_assistant(member.chat.id)
        get = await app.get_chat_member(chat_id, userbot.id)
        if get.status in [ChatMemberStatus.BANNED]:

            # Assistant bot has been banned
            remove_by = member.from_user.mention if member.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
            chat_id = member.chat.id
            title = member.chat.title
            username = (
                f"@{member.chat.username}" if member.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
            )

            # Construct message
            left_message = (
                f"╔══❰#𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁_𝗕𝗮𝗻𝗻𝗲𝗱❱══❍⊱❁۪۪\n║\n"
                f"║┣⪼ <b>𝐂ʜᴀᴛ »</b> {title}\n║\n"
                f"║┣⪼ <b>𝐀ssɪsᴛᴀɴᴛ 𝐈ᴅ »</b> {userbot.id}\n║\n"
                f"║┣⪼ <b>𝐍ᴀᴍᴇ »</b> @{userbot.username}\n║\n"
                f"║┣⪼ <b>𝐁ᴀɴ 𝐁ʏ »</b> {remove_by}\n"
                f"╚══════════════════❍⊱❁"
            )

            # Create keyboard for unban button
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✨𝐔𝐧𝐛𝐚𝐧 𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭✨",
                            callback_data="unban_userbot",
                        )
                    ]
                ]
            )

            # Send photo with the left message and keyboard
            await app.send_photo(
                chat_id,
                photo=random.choice(photo),
                caption=left_message,
                reply_markup=keyboard,
            )
            # Perform actions like stopping streams or loops
            await ERA.stop_stream(chat_id)
            await set_loop(chat_id, 0)
            await app.unban_chat_member(chat_id, userbot.id)
            await asyncio.sleep(10)
    except UserNotParticipant:
        await ERA.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await app.unban_chat_member(chat_id, userbot.id)
        await asyncio.sleep(10)
        return
    except Exception as e:
        return


@app.on_chat_member_updated(filters.group, group=-8)
async def assistant_left(client: app, member: ChatMemberUpdated):
    chat_id = member.chat.id
    try:
        userbot = await get_assistant(chat_id)
        userbot_id = userbot.id

        # Check if the leaving member is the userbot
        if (
            not member.new_chat_member
            and member.old_chat_member.user.id == userbot_id
            and member.old_chat_member.status not in {"banned", "left", "restricted"}
            and member.old_chat_member
        ):
            left_message = (
                f"<b>Assistant Has Left This Chat</b>\n\n"
                f"<b>Id:</b> `{userbot.id}`\n"
                f"<b>Name:</b> @{userbot.username}\n\n"
                f"<b>Invite Assistant By: /userbotjoin</b>"
            )
            await app.send_photo(
                chat_id,
                photo=random.choice(photo),
                caption=left_message,
                reply_markup=keyboard,
            )

            await ERA.stop_stream(chat_id)
            await set_loop(chat_id, 0)
            await asyncio.sleep(10)
    except UserNotParticipant:
        left_message = (
            f"<b>Assistant Has Left This Chat<b>\n\n"
            f"<b>Id:<b> `{userbot.id}`\n"
            f"<b>Name:<b> @{userbot.username}\n\n"
            f"<b>Invite Assistant By: /userbotjoin<b>"
        )
        await app.send_photo(
            chat_id,
            photo=random.choice(photo),
            caption=left_message,
            reply_markup=keyboard,
        )
        await ERA.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await asyncio.sleep(10)
    except Exception as e:
        return


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
