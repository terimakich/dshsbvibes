import os
import requests
from pyrogram import Client, filters
from ERAVIBES import app

def fetch_song(song_name):
    url = f"https://song-teleservice.vercel.app/song?songName={song_name.replace(' ', '%20')}"
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 and "downloadLink" in response.json() else None
    except Exception as e:
        print(f"API Error: {e}")
        return None

@app.on_message(filters.command("song"))
async def handle_song(client, message):
    song_name = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None
    if not song_name:
        return await message.reply("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ ᴀғᴛᴇʀ ᴛʜᴇ /song ᴄᴏᴍᴍᴀɴᴅ..")

    song_info = fetch_song(song_name)
    if not song_info:
        return await message.reply(f"sᴏʀʀʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ғɪɴᴅ ᴛʜᴇ sᴏɴɢ '{song_name}'.")

    filename = f"{song_info['trackName']}.mp3"
    download_url = song_info['downloadLink']

    # Download and save the file
    with requests.get(download_url, stream=True) as r, open(filename, "wb") as file:
        for chunk in r.iter_content(1024):
            if chunk:
                file.write(chunk)

    caption = (f"""❖ sᴏɴɢ ɴᴀᴍᴇ ➥ {song_info['trackName']}\n\n● ᴀʟʙᴜᴍ ➥ {song_info['album']}\n ● ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ ➥ {song_info['releaseDate']}\n● ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ ➥ {message.from_user.mention}\n❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ  ➥ ˹ 𝐊ʀɪsʜ ꭙ ᴍᴜsɪᴄ™""")

    # Send audio and clean up
    await message.reply_audio(audio=open(filename, "rb"), caption=caption)
    os.remove(filename)
