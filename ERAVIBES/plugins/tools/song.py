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

