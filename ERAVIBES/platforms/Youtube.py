import asyncio, aiohttp, os, re, json, random, glob, logging
from typing import Union, Tuple

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from ERAVIBES.utils.database import is_on_off
from ERAVIBES.utils.formatters import time_to_seconds
from config import API_URL, API_KEY

_info_cache = {}

def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    
    if not os.path.exists(cookie_dir):
        os.makedirs(cookie_dir)
        raise FileNotFoundError("Cookies folder was not found, so it has been created. Please add your cookie .txt files.")

    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        raise FileNotFoundError("No .txt files found in the cookies folder.")

    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

def extract_video_info(link: str) -> dict:
    if link in _info_cache:
        return _info_cache[link]
    
    ytdl_opts = {
        "quiet": True,
        "cookiefile": cookie_txt_file(),
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
    
    _info_cache[link] = info
    return info

async def api_download_song(video_id: str) -> Union[str, None]:
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    for ext in ["mp3", "m4a", "webm"]:
        file_path = os.path.join(download_folder, f"{video_id}.{ext}")
        if os.path.exists(file_path):
            return file_path
            
    song_url = f"{API_URL}/song/{video_id}?api={API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        for attempt in range(10):
            try:
                async with session.get(song_url) as response:
                    if response.status != 200:
                        await asyncio.sleep(4)
                        continue
                    
                    data = await response.json()
                    status = data.get("status", "").lower()

                    if status == "done":
                        download_url = data.get("link")
                        if not download_url:
                            return None
                        
                        file_format = data.get("format", "mp3").lower()
                        file_name = f"{video_id}.{file_format}"
                        file_path = os.path.join(download_folder, file_name)

                        async with session.get(download_url) as file_response:
                            if file_response.status == 200:
                                with open(file_path, 'wb') as f:
                                    while True:
                                        chunk = await file_response.content.read(8192)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                                return file_path
                            else:
                                return None

                    elif status == "downloading":
                        await asyncio.sleep(4)
                    else:
                        return None
            except Exception:
                return None
        else:
            return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(r"(?:youtube\.com|youtu\.be)")
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + link
        return bool(self.regex.search(link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        
        text = ""
        offset = None
        length = None
        
        for msg in messages:
            if offset is not None:
                break
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        offset, length = entity.offset, entity.length
                        break
            elif msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        
        if offset is None:
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None) -> Union[Tuple[str, str, int, str, str], None]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            results = VideosSearch(link, limit=1)
            search_result = (await results.next())["result"][0]
            
            title = search_result["title"]
            duration_str = search_result["duration"]
            thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
            vidid = search_result["id"]
            duration_sec = int(time_to_seconds(duration_str)) if duration_str else 0
            
            return title, duration_str, duration_sec, thumbnail, vidid
        except IndexError:
            return None

    async def track(self, link: str, videoid: Union[bool, str] = None) -> Union[Tuple[dict, str], None]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            results = VideosSearch(link, limit=1)
            search_result = (await results.next())["result"][0]
            track_details = {
                "title": search_result["title"],
                "link": search_result["link"],
                "vidid": search_result["id"],
                "duration_min": search_result["duration"],
                "thumb": search_result["thumbnails"][0]["url"].split("?")[0],
            }
            return track_details, search_result["id"]
        except IndexError:
            return None

    async def playlist(self, link: str, limit: int, user_id, videoid: Union[bool, str] = None) -> list:
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        def get_playlist_ids():
            ytdl_opts = {
                "quiet": True, 
                "cookiefile": cookie_txt_file(),
                "extract_flat": "in_playlist",
                "playlistend": limit,
            }
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return [entry.get("id") for entry in info.get("entries", []) if entry.get("id")]

        return await asyncio.to_thread(get_playlist_ids)

    async def download(self, link: str, mystic, video: bool = False,
                       videoid: bool = False, songaudio: bool = False,
                       songvideo: bool = False, format_id: str = None,
                       title: str = None) -> Union[Tuple[str, bool], None]:
        
        vid_id = None
        if videoid:
            vid_id = link
            link = self.base + link
        else:
            match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", link)
            if match:
                vid_id = match.group(1)

        loop = asyncio.get_running_loop()

        def song_dl(is_video: bool):
            fpath = f"downloads/{title}"
            formats_opt = f"{format_id}+140" if is_video else format_id
            
            ydl_opts = {
                "format": formats_opt,
                "outtmpl": fpath if is_video else f"{fpath}.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_txt_file(),
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4" if is_video else None,
            }
            if not is_video:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_dl, True)
            return f"downloads/{title}.mp4", True
        elif songaudio:
            await loop.run_in_executor(None, song_dl, False)
            return f"downloads/{title}.mp3", True
        
        downloaded_file = None
        direct = True

        if not video:
            if vid_id:
                downloaded_file = await api_download_song(vid_id)
            
            if not downloaded_file:
                def audio_dl_fallback():
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": "downloads/%(id)s.%(ext)s",
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "quiet": True,
                        "cookiefile": cookie_txt_file(),
                        "no_warnings": True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(link, download=False)
                        fpath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                        if os.path.exists(fpath):
                            return fpath
                        ydl.download([link])
                        return fpath
                downloaded_file = await loop.run_in_executor(None, audio_dl_fallback)
        
        else:
            def video_dl():
                ydl_opts = {
                    "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "cookiefile": cookie_txt_file(),
                    "no_warnings": True,
                    "merge_output_format": "mp4",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    fpath = os.path.join("downloads", f"{info['id']}.mp4")
                    if os.path.exists(fpath):
                        return fpath
                    ydl.download([link])
                    return fpath
            downloaded_file = await loop.run_in_executor(None, video_dl)

        return downloaded_file, direct
