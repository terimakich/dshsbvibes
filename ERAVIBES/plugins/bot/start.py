import logging
import traceback
import time
import random 
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from ERAVIBES import app
from ERAVIBES.misc import _boot_
from ERAVIBES.plugins.sudo.sudoers import sudoers_list
from ERAVIBES.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    is_served_private_chat,
)
from ERAVIBES.utils.decorators.language import LanguageStart
from ERAVIBES.utils.formatters import get_readable_time
from ERAVIBES.utils.inline import help_pannel, private_panel, start_pannel
from config import BANNED_USERS, START_IMG_URL, D
from strings import get_string, image


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    await message.react(random.choice(D))
        
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(image),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"❖ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>● ᴜsᴇʀ ɪᴅ ➥</b> <code>{message.from_user.id}</code>\n<b>● ᴜsᴇʀɴᴀᴍᴇ ➥</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"❖ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>● ᴜsᴇʀ ɪᴅ ➥</b> <code>{message.from_user.id}</code>\n<b>● ᴜsᴇʀɴᴀᴍᴇ ➥</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        await message.reply_photo(
            random.choice(image),
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"❖ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>● ᴜsᴇʀ ɪᴅ ➥</b> <code>{message.from_user.id}</code>\n<b>● ᴜsᴇʀɴᴀᴍᴇ ➥</b> @{message.from_user.username}",
            )



@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    try:
        # React with random emoji
        await message.react(random.choice(D))
    except Exception as e:
        print(f"Reaction Error: {e}")

    try:
        # Create Inline keyboard button with link
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("𝗺𝘆 𝗼𝘄𝗻𝗲𝗿", url="https://t.me/DvisDmBot?start")]
        ])

        # Send message with inline keyboard
        await message.reply_text(
            "<blockquote>❍ Hᴇʏ ʙᴀʙʏ :) ɴᴇᴇᴅ ʜᴇʟᴘ? ʀᴇᴀᴄʜ ᴏᴜᴛ ᴛᴏ</blockquote>",
            quote=True,
            reply_markup=keyboard
        )
        print("Reply sent successfully.")
    except Exception as e:
        print(f"Reply Error: {e}")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_message(filters.new_chat_members, group=3)
async def welcome(client, message: Message):
    chat_id = message.chat.id

    # Private bot mode check
    if config.PRIVATE_BOT_MODE:
        if not await is_served_private_chat(chat_id):
            await message.reply_text(
                "<b>ᴛʜɪs ʙᴏᴛ's ᴘʀɪᴠᴀᴛᴇ ᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ. ᴏɴʟʏ ᴍʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs. ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ɪᴛ ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ, ᴀsᴋ ᴍʏ ᴏᴡɴᴇʀ ᴛᴏ ᴀᴜᴛʜᴏʀɪᴢᴇ ʏᴏᴜʀ ᴄʜᴀᴛ.</b>"
            )
            return await client.leave_chat(chat_id)
    else:
        await add_served_chat(chat_id)

    # Handle new chat members
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)

            # If bot itself joins the chat
            if member.id == client.id:
                try:
                    groups_photo = await client.download_media(
                        message.chat.photo.big_file_id, file_name=f"chatpp{chat_id}.png"
                    )
                    chat_photo = groups_photo if groups_photo else START_IMG_URL
                except AttributeError:
                    chat_photo = START_IMG_URL

                userbot = await get_assistant(chat_id)
                out = start_pannel(_)
                await message.reply_photo(
                    photo=chat_photo,
                    caption=_["start_9"],
                    reply_markup=InlineKeyboardMarkup(out),
                )

            # Handle owner joining
            if member.id in config.OWNER_ID:
                await message.reply_text(
                    _["start_7"].format(client.mention, member.mention)
                )
                continue

            # Handle SUDOERS joining
            if member.id in SUDOERS:
                await message.reply_text(
                    _["start_8"].format(client.mention, member.mention)
                )
                continue

        except Exception as e:
            logger.error(f"Error: {e}\nTraceback: {traceback.format_exc()}")
            continue

@app.on_callback_query(filters.regex("go_to_start"))
@LanguageStart
async def go_to_home(client, callback_query: CallbackQuery, _):
    try:
        out = music_start_pannel(_)
        await callback_query.message.edit_text(
            text=_["start_9"].format(callback_query.message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
    except Exception as e:
        logger.error(f"Error editing message: {e}")
