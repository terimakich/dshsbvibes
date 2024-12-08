import yt_dlp as youtube_dl
from pyrogram import Client, filters
from youtubesearchpython import VideosSearch
form ERAVIBES import app

def download_youtube_audio(url: str, download_path: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')
    return audio_file

@app.on_message(filters.command("song"))
def song(client, message):
    query = message.text.split(maxsplit=1)[1]  # Extract song name from the message
    message.reply_text('Searching for the song...')
    
    # Search for the song on YouTube
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    video_url = result['result'][0]['link']
    
    try:
        audio_file = download_youtube_audio(video_url, '/path/to/download')
        message.reply_text('Download complete. Sending audio...')
        message.reply_audio(audio=open(audio_file, 'rb'))
    except Exception as e:
        message.reply_text(f'Error: {str(e)}')







"""import os
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

    caption = (f"""❖ sᴏɴɢ ɴᴀᴍᴇ ➥ {song_info['trackName']}\n\n● ᴀʟʙᴜᴍ ➥ {song_info['album']}\n ● ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ ➥ {song_info['releaseDate']}\n● ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ ➥ {message.from_user.mention}\n❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ  ➥ ˹ ᴇʀᴀ ꭙ ᴠɪʙᴇs™ ♡゙""")

    # Send audio and clean up
    await message.reply_audio(audio=open(filename, "rb"), caption=caption)
    os.remove(filename)"""
