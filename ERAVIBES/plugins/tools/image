import os
import shutil
import asyncio
from re import findall
from bing_image_downloader import downloader
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message
from ERAVIBES import app

@app.on_message(filters.command(["img", "image"], prefixes=["/", "!", "", "."]))
async def google_img_search(client: Client, message: Message):
    chat_id = message.chat.id
    command_message_id = message.id  # ID of the command message

    try:
        query = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply("❍ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ɪᴍᴀɢᴇ ǫᴜᴇʀʏ ᴛᴏ sᴇᴀʀᴄʜ!")

    lim = findall(r"lim=\d+", query)
    try:
        lim = int(lim[0].replace("lim=", ""))
        query = query.replace(f"lim={lim}", "")
    except IndexError:
        lim = 6  # Default limit to 6 images

    download_dir = "downloads"

    try:
        downloader.download(query, limit=lim, output_dir=download_dir, adult_filter_off=True, force_replace=False, timeout=60)
        images_dir = os.path.join(download_dir, query)
        if not os.listdir(images_dir):
            raise Exception("No images were downloaded.")
        lst = [os.path.join(images_dir, img) for img in os.listdir(images_dir)][:lim]  # Ensure we only take the number of images specified by lim
    except Exception as e:
        return await message.reply(f"❍ ᴇʀʀᴏʀ ɪɴ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇs: {e}")

    msg = await message.reply("❍ ғɪɴᴅɪɴɢ ɪᴍᴀɢᴇs.....")

    count = 0
    for img in lst:
        count += 1
        await msg.edit(f"❍ ғɪɴᴅ {count} ɪᴍᴀɢᴇs.....")

    try:
        media_group = await app.send_media_group(
            chat_id=chat_id,
            media=[InputMediaPhoto(media=img) for img in lst],
            reply_to_message_id=command_message_id
        )
        await msg.delete()

        # Schedule cleanup after 2 minutes
        await asyncio.sleep(120)

        # Delete media messages
        for media_msg in media_group:
            await app.delete_messages(chat_id, media_msg.id)

        # Delete command message
        await app.delete_messages(chat_id, [command_message_id])

        # Cleanup: Delete all images in the downloads folder
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)  # Deletes the entire downloads directory

    except Exception as e:
        await msg.delete()
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)  # Cleanup all images even if an error occurs
        return await message.reply(f"❍ ᴇʀʀᴏʀ ɪɴ sᴇɴᴅɪɴɢ ɪᴍᴀɢᴇs: {e}")
