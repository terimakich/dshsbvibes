import asyncio
import os
import re
import json
import glob
import random
import aiohttp # For asynchronous HTTP requests to the new API
import requests # Kept for existing uses, if any
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
import config # Assuming this is used elsewhere in the larger project
from ERAVIBES.utils.database import is_on_off # Assuming this utility exists
from ERAVIBES.utils.formatters import time_to_seconds
# from ytdlx import ytdlx # Not used in the provided snippet, kept for completeness if part of a larger project

def cookie_txt_file():
    """
    Randomly selects a .txt cookie file from the 'cookies' folder
    and logs its selection.
    """
    folder_path = f"{os.getcwd()}/cookies"
    filename = f"{os.getcwd()}/cookies/logs.csv"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        # If no .txt files are found, raise an error.
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_file = random.choice(txt_files)
    with open(filename, 'a') as file:
        file.write(f'Choosen File : {cookie_file}\n')
    return f"cookies/{os.path.basename(cookie_file)}"

async def check_file_size(link):
    """
    Checks the total size of a YouTube video/audio link using yt-dlp.
    This is used to determine if a file is too large for direct download.
    """
    async def get_format_info(link):
        """Helper to get format info from yt-dlp in JSON format."""
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J", # Output JSON
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error getting format info for {link}:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        """Parses the total filesize from yt-dlp formats."""
        total_size = 0
        for fmt in formats:
            if 'filesize' in fmt and fmt['filesize']:
                total_size += fmt['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    formats = info.get('formats', [])
    if not formats:
        print(f"No formats found for {link}.")
        return None
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    """
    Executes a shell command asynchronously and returns its stdout/stderr.
    """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        # Handle specific yt-dlp error messages
        if "unavailable videos are hidden" in errorz.decode("utf-8").lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

async def _download_from_maybechiku_api(link: str, file_extension: str, vid_id: str = None):
    """
    Attempts to download video/audio using the maybechiku API.
    This API provides direct download links.
    
    Args:
        link (str): The YouTube video URL.
        file_extension (str): The desired file extension (e.g., "mp3", "mp4").
        vid_id (str, optional): The YouTube video ID. If not provided, it will be extracted from the link.

    Returns:
        tuple: (file_path: str, direct: bool) on success, (None, False) on failure.
               'direct' is True if downloaded directly, False otherwise.
    """
    maybechiku_base_url = "[https://youtube.maybechiku.workers.dev/](https://youtube.maybechiku.workers.dev/)"
    query_string = {"url": link}

    # If vid_id is not provided, try to extract it from the link
    if not vid_id:
        match = re.search(r'(?:youtu\.be\/|youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})', link)
        if match:
            vid_id = match.group(1)
        else:
            vid_id = "unknown_id" # Fallback ID if extraction fails

    file_path = os.path.join("downloads", f"{vid_id}.{file_extension}")

    # Check if file already exists locally to avoid re-downloading
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return file_path, True

    async with aiohttp.ClientSession() as session:
        try:
            # Make a GET request to the maybechiku API
            async with session.get(maybechiku_base_url, params=query_string) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                data = await response.json()

                # Check if the API call was successful and a downloadURL is provided
                if data.get('success') and data.get('data') and data['data'].get('downloadURL'):
                    download_url = data['data']['downloadURL']
                    print(f"Attempting to download from Maybechiku API: {download_url}")
                    
                    # Download the file from the obtained URL
                    async with session.get(download_url) as file_response:
                        file_response.raise_for_status() # Check for errors during file download
                        os.makedirs("downloads", exist_ok=True) # Ensure downloads directory exists
                        with open(file_path, "wb") as f:
                            while True:
                                chunk = await file_response.content.read(8192) # Read in chunks for large files
                                if not chunk:
                                    break
                                f.write(chunk)
                        print(f"Successfully downloaded via maybechiku API: {file_path}")
                        return file_path, True # downloaded_file, direct download
                else:
                    print(f"Maybechiku API reports failure or missing downloadURL for {link}: {data}")
                    return None, False # API failed, so no file and not direct
        except aiohttp.ClientError as e:
            print(f"Maybechiku API AIOHTTP error for {link}: {e}")
            return None, False
        except json.JSONDecodeError as e:
            print(f"Maybechiku API JSON decode error for {link}: {e}")
            return None, False
        except Exception as e:
            print(f"An unexpected error occurred with Maybechiku API for {link}: {e}")
            return None, False


class YouTubeAPI:
    """
    A class to interact with YouTube for fetching video details,
    playlists, and downloading content.
    """
    def __init__(self):
        self.base = "[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)"
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "[https://www.youtube.com/oembed?url=](https://www.youtube.com/oembed?url=)"
        self.listbase = "[https://youtube.com/playlist?list=](https://youtube.com/playlist?list=)"
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        """Checks if a given link is a valid YouTube link."""
        if videoid:
            link = self.base + link
        return True if re.search(self.regex, link) else False
    
    async def url(self, message_1: Message) -> Union[str, None]:
        """Extracts a URL from a Pyrogram Message object."""
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == "text_link":
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]
    
    async def details(self, link: str, videoid: Union[bool, str] = None):
        """Fetches detailed information about a YouTube video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
            return title, duration_min, duration_sec, thumbnail, vidid
    
    async def title(self, link: str, videoid: Union[bool, str] = None):
        """Fetches the title of a YouTube video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["title"]
    
    async def duration(self, link: str, videoid: Union[bool, str] = None):
        """Fetches the duration of a YouTube video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["duration"]
    
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        """Fetches the thumbnail URL of a YouTube video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
    
    async def video(self, link: str, videoid: Union[bool, str] = None):
        """
        Retrieves a direct streaming URL for a YouTube video (up to 720p/1280p).
        Returns 1 and URL on success, 0 and error on failure.
        """
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-g", # Get direct URL
            "-f", # Format selection
            "best[height<=?720][width<=?1280]", # Best video up to 720p resolution
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()
    
    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        """Fetches video IDs from a YouTube playlist."""
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        # Use shell_cmd to get playlist IDs without downloading
        playlist_ids = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {link}"
        )
        return [pid for pid in playlist_ids.split("\n") if pid.strip() != ""]
    
    async def track(self, link: str, videoid: Union[bool, str] = None):
        """Fetches details of a single track/video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            track_details = {
                "title": result["title"],
                "link": result["link"],
                "vidid": result["id"],
                "duration_min": result["duration"],
                "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }
            return track_details, result["id"]
    
    async def formats(self, link: str, videoid: Union[bool, str] = None):
        """Fetches available formats for a YouTube video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            info = ydl.extract_info(link, download=False)
            for fmt in info.get("formats", []):
                try:
                    str(fmt["format"])
                except:
                    continue
                # Exclude dash formats and ensure essential keys are present
                if "dash" not in str(fmt["format"]).lower():
                    try:
                        fmt["format"]
                        fmt["filesize"]
                        fmt["format_id"]
                        fmt["ext"]
                        fmt["format_note"]
                    except:
                        continue
                    formats_available.append({
                        "format": fmt["format"],
                        "filesize": fmt["filesize"],
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "format_note": fmt["format_note"],
                        "yturl": link,
                    })
            return formats_available, link
    
    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        """Fetches details for video suggestions (slider)."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        results_dict = await a.next()
        result = results_dict.get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid
    
    async def download(self, link: str, mystic, video: Union[bool, str] = None,
                       videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None,
                       songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None,
                       title: Union[bool, str] = None):
        """
        Downloads YouTube video or audio content.
        Prioritizes the maybechiku API for faster downloads, falls back to yt-dlp.
        """
        
        # Determine the full YouTube link to use for download operations
        if videoid:
            full_link = self.base + videoid
        else:
            full_link = link
        
        downloaded_file = None
        direct = False # Indicates if a direct file path is returned or a streaming URL

        if songvideo and format_id and title:
            # Case: Specific video format download (e.g., from a /formats command)
            file_ext = "mp4"
            # Try maybechiku API first for speed
            downloaded_file, direct = await _download_from_maybechiku_api(full_link, file_ext, videoid)
            
            if not downloaded_file: # Fallback to yt-dlp if new API fails or file not found
                print(f"Maybechiku API failed for {full_link} (songvideo). Falling back to yt-dlp.")
                loop = asyncio.get_running_loop()
                def song_video_dl_sync():
                    # Sanitize title for safe filename usage
                    safe_title = re.sub(r'[^\w\-_\.]', '', str(title))
                    fpath = f"downloads/{safe_title}"
                    ydl_opts = {
                        "format": f"{format_id}+140", # Combine video and audio stream
                        "outtmpl": fpath, # Output template for downloaded file
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "quiet": True,
                        "no_warnings": True,
                        "cookiefile": cookie_txt_file(),
                        "prefer_ffmpeg": True, # Prefer ffmpeg for merging
                        "merge_output_format": "mp4", # Ensure output is mp4
                    }
                    x = yt_dlp.YoutubeDL(ydl_opts)
                    x.download([full_link])
                    
                    # After download, yt-dlp might append extension, so construct final path
                    final_path = f"{fpath}.mp4"
                    if os.path.exists(final_path):
                        return final_path
                    # Fallback to glob if exact filename not found due to potential variations
                    glob_path = glob.glob(f"downloads/{safe_title}*.mp4")
                    return glob_path[0] if glob_path else None
                downloaded_file = await loop.run_in_executor(None, song_video_dl_sync)
                direct = True # yt-dlp local download is always direct

        elif songaudio and format_id and title:
            # Case: Specific audio format download (e.g., from a /formats command)
            file_ext = "mp3"
            # Try maybechiku API first for speed
            downloaded_file, direct = await _download_from_maybechiku_api(full_link, file_ext, videoid)
            
            if not downloaded_file: # Fallback to yt-dlp if new API fails or file not found
                print(f"Maybechiku API failed for {full_link} (songaudio). Falling back to yt-dlp.")
                loop = asyncio.get_running_loop()
                def song_audio_dl_sync():
                    safe_title = re.sub(r'[^\w\-_\.]', '', str(title))
                    fpath = f"downloads/{safe_title}.%(ext)s" # Output template for downloaded file
                    ydl_opts = {
                        "format": format_id, # Use specific audio format ID
                        "outtmpl": fpath,
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "quiet": True,
                        "no_warnings": True,
                        "cookiefile": cookie_txt_file(),
                        "prefer_ffmpeg": True,
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192", # High quality mp3
                            }
                        ],
                    }
                    x = yt_dlp.YoutubeDL(ydl_opts)
                    x.download([full_link])
                    
                    # After download, find the actual .mp3 file generated by postprocessor
                    actual_file = glob.glob(f"downloads/{safe_title}*.mp3")
                    return actual_file[0] if actual_file else None
                downloaded_file = await loop.run_in_executor(None, song_audio_dl_sync)
                direct = True # yt-dlp local download is always direct

        elif video:
            # Case: General video download (best quality up to 720p/1280p)
            file_ext = "mp4"
            # Try maybechiku API first
            downloaded_file, direct = await _download_from_maybechiku_api(full_link, file_ext, videoid)
            
            if not downloaded_file: # Fallback to yt-dlp if new API fails or file not found
                print(f"Maybechiku API failed for {full_link} (video). Falling back to yt-dlp.")
                if await is_on_off(1): # Check if direct download (local server download) is enabled
                    loop = asyncio.get_running_loop()
                    def video_dl_sync():
                        ydl_opts = {
                            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])", # Prioritize 720p mp4
                            "outtmpl": f"downloads/%(id)s.%(ext)s", # Use video ID for filename
                            "geo_bypass": True,
                            "nocheckcertificate": True,
                            "quiet": True,
                            "cookiefile": cookie_txt_file(),
                            "no_warnings": True,
                        }
                        x = yt_dlp.YoutubeDL(ydl_opts)
                        info = x.extract_info(full_link, download=False)
                        xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                        if os.path.exists(xyz): # Check if already downloaded by yt-dlp
                            return xyz
                        x.download([full_link])
                        return xyz
                    downloaded_file = await loop.run_in_executor(None, video_dl_sync)
                    direct = True # yt-dlp local download is always direct
                else:
                    # Fallback: Get direct streaming URL from yt-dlp or check file size
                    proc = await asyncio.create_subprocess_exec(
                        "yt-dlp",
                        "--cookies", cookie_txt_file(),
                        "-g", # Get direct URL
                        "-f",
                        "best[height<=?720][width<=?1280]",
                        full_link,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await proc.communicate()
                    if stdout:
                        downloaded_file = stdout.decode().split("\n")[0]
                        direct = False # This is a streaming URL, not a local file
                    else:
                        print(f"yt-dlp failed to get direct URL for {full_link}. Checking file size...")
                        file_size = await check_file_size(full_link)
                        if not file_size:
                            print("File size could not be determined.")
                            return None, False
                        total_size_mb = file_size / (1024 * 1024)
                        if total_size_mb > 250: # Enforce 250MB limit
                            print(f"File size {total_size_mb:.2f} MB exceeds the 250MB limit. Not downloading.")
                            return None, False
                        
                        # If size is okay but direct URL failed, force local download via yt-dlp
                        print(f"File size {total_size_mb:.2f} MB is within limit. Forcing local yt-dlp download.")
                        loop = asyncio.get_running_loop()
                        def video_dl_sync_fallback_size():
                            ydl_opts = {
                                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                                "outtmpl": f"downloads/%(id)s.%(ext)s",
                                "geo_bypass": True,
                                "nocheckcertificate": True,
                                "quiet": True,
                                "cookiefile": cookie_txt_file(),
                                "no_warnings": True,
                            }
                            x = yt_dlp.YoutubeDL(ydl_opts)
                            info = x.extract_info(full_link, download=False)
                            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                            if os.path.exists(xyz):
                                return xyz
                            x.download([full_link])
                            return xyz
                        downloaded_file = await loop.run_in_executor(None, video_dl_sync_fallback_size)
                        direct = True # This is a local file

        else: # Case: General audio download (best quality)
            file_ext = "mp3"
            # Try maybechiku API first for speed
            downloaded_file, direct = await _download_from_maybechiku_api(full_link, file_ext, videoid)
            
            if not downloaded_file: # Fallback to yt-dlp if new API fails or file not found
                print(f"Maybechiku API failed for {full_link} (audio). Falling back to yt-dlp.")
                loop = asyncio.get_running_loop()
                def audio_dl_sync():
                    ydl_opts = {
                        "format": "bestaudio/best", # Get best audio
                        "outtmpl": f"downloads/%(id)s.%(ext)s", # Use video ID for filename
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "quiet": True,
                        "no_warnings": True,
                        "cookiefile": cookie_txt_file(),
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio", # Extract audio
                                "preferredcodec": "mp3", # Convert to mp3
                                "preferredquality": "192",
                            }
                        ],
                    }
                    x = yt_dlp.YoutubeDL(ydl_opts)
                    info = x.extract_info(full_link, download=False)
                    
                    # yt-dlp will download and convert, so find the final .mp3 file
                    final_audio_path = os.path.join("downloads", f"{info['id']}.mp3")
                    if os.path.exists(final_audio_path):
                        return final_audio_path
                    x.download([full_link])
                    # After download, glob to find the actual mp3 file (might have slightly different name)
                    actual_file = glob.glob(f"downloads/{info['id']}*.mp3")
                    return actual_file[0] if actual_file else None
                downloaded_file = await loop.run_in_executor(None, audio_dl_sync)
                direct = True # yt-dlp local download is always direct

        return downloaded_file, direct
