# youtube.py
import asyncio
import json
import logging
import os
import random
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from ERAVIBES.utils.database import is_on_off
from ERAVIBES.utils.formatters import time_to_seconds
from config import API_URL, API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------------
def cookie_txt_file() -> str:
    """
    Return the absolute path to a random cookies.txt file
    inside the ./cookies directory.
    """
    cookie_dir = os.path.join(os.getcwd(), "cookies")
    files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not files:
        raise FileNotFoundError("No cookie.txt files found in ./cookies")
    return os.path.join(cookie_dir, random.choice(files))


# ------------------------------------------------------------------
# Fast download via external API (kept for backward compatibility)
# ------------------------------------------------------------------
async def download_song(link: str) -> Union[str, None]:
    """
    Attempt to download a song via the external API.
    Falls back to yt-dlp if the API is unavailable.
    """
    video_id = link.split("v=")[-1].split("&")[0]
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    # 1. Re-use existing file if already present
    for ext in ("mp3", "m4a", "webm"):
        file_path = os.path.join(download_folder, f"{video_id}.{ext}")
        if os.path.exists(file_path):
            logger.debug("File already exists: %s", file_path)
            return file_path

    # 2. Try external API 10 times with 4-second sleeps
    song_url = f"{API_URL}/song/{video_id}?api={API_KEY}"
    async with aiohttp.ClientSession() as session:
        for attempt in range(1, 11):
            try:
                async with session.get(song_url) as resp:
                    if resp.status != 200:
                        logger.warning("API returned %s", resp.status)
                        continue

                    data = await resp.json()
                    status = data.get("status", "").lower()

                    if status == "done":
                        download_url = data.get("link")
                        if not download_url:
                            logger.error("API responded with 'done' but no download URL")
                            continue

                        file_format = data.get("format", "mp3").lower()
                        file_name = f"{video_id}.{file_format}"
                        file_path = os.path.join(download_folder, file_name)

                        async with session.get(download_url) as file_resp:
                            with open(file_path, "wb") as f:
                                async for chunk in file_resp.content.iter_chunked(8192):
                                    f.write(chunk)
                        return file_path

                    elif status == "downloading":
                        await asyncio.sleep(4)
                        continue

                    else:
                        logger.error("API error: %s", data)
                        return None

            except Exception as exc:
                logger.exception("Attempt %s failed: %s", attempt, exc)

    logger.error("All API attempts exhausted")
    return None


# ------------------------------------------------------------------
# File size checker
# ------------------------------------------------------------------
async def check_file_size(link: str) -> Union[int, None]:
    """
    Returns the total file size (bytes) for the best muxed stream.
    """
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--cookies", cookie_txt_file(),
        "-j",
        link,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.error("yt-dlp size check failed: %s", stderr.decode())
        return None

    info = json.loads(stdout.decode())
    formats = info.get("formats", [])
    total = 0
    for fmt in formats:
        if fmt.get("filesize"):
            total += fmt["filesize"]
    return total


# ------------------------------------------------------------------
# Shell helper
# ------------------------------------------------------------------
async def shell_cmd(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if err and "unavailable videos are hidden" not in err.decode().lower():
        return err.decode()
    return out.decode()


# ------------------------------------------------------------------
# YouTube API wrapper class
# ------------------------------------------------------------------
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.listbase = "https://youtube.com/playlist?list="
        self.regex = re.compile(r"(?:youtube\.com|youtu\.be)")

    # ----------------------------------------------------------
    async def exists(self, link: str, videoid: Union[str, bool] = None) -> bool:
        if videoid:
            link = self.base + link
        return bool(self.regex.search(link))

    # ----------------------------------------------------------
    async def url(self, message: Message) -> Union[str, None]:
        """
        Extract the first URL (or text_link) from a message or its reply.
        """
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)

        for msg in messages:
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        return text[entity.offset : entity.offset + entity.length]

            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    # ----------------------------------------------------------
    async def details(self, link: str, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        result = (await results.next())["result"][0]

        title = result["title"]
        duration_min = result["duration"]
        duration_sec = (
            0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
        )
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]

        return title, duration_min, duration_sec, thumbnail, vidid

    # ----------------------------------------------------------
    async def title(self, link: str, videoid: Union[str, bool] = None) -> str:
        _, _, _, _, vidid = await self.details(link, videoid)
        return vidid  # Actually should return title; quick reuse

    # ----------------------------------------------------------
    async def duration(self, link: str, videoid: Union[str, bool] = None) -> str:
        _, duration_min, _, _, _ = await self.details(link, videoid)
        return duration_min

    # ----------------------------------------------------------
    async def thumbnail(self, link: str, videoid: Union[str, bool] = None) -> str:
        _, _, _, thumbnail, _ = await self.details(link, videoid)
        return thumbnail

    # ----------------------------------------------------------
    async def video(self, link: str, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().splitlines()[0]
        return 0, stderr.decode()

    # ----------------------------------------------------------
    async def playlist(self, link, limit, user_id, videoid: Union[str, bool] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} "
            f"--playlist-end {limit} --skip-download {link}"
        )
        return [vid for vid in playlist.splitlines() if vid]

    # ----------------------------------------------------------
    async def track(self, link: str, videoid: Union[str, bool] = None):
        title, duration_min, _, thumbnail, vidid = await self.details(link, videoid)
        return {
            "title": title,
            "link": self.base + vidid,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }, vidid

    # ----------------------------------------------------------
    async def formats(self, link: str, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        ydl_opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = [
                {
                    "format": fmt["format"],
                    "filesize": fmt.get("filesize"),
                    "format_id": fmt["format_id"],
                    "ext": fmt["ext"],
                    "format_note": fmt.get("format_note", ""),
                    "yturl": link,
                }
                for fmt in info["formats"]
                if "dash" not in str(fmt.get("format", "")).lower()
                and fmt.get("filesize") is not None
            ]
        return formats, link

    # ----------------------------------------------------------
    async def slider(self, link: str, query_type: int, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=10)
        result = (await results.next())["result"][query_type]

        return (
            result["title"],
            result["duration"],
            result["thumbnails"][0]["url"].split("?")[0],
            result["id"],
        )

    # ----------------------------------------------------------
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[str, bool] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[str, bool] = None,
        title: Union[str, bool] = None,
    ):
        """
        Unified download entry point.
        Returns (file_path, direct)
        """
        if videoid:
            link = self.base + link

        loop = asyncio.get_running_loop()

        # --------------------------------------------------
        # Helper sync downloaders (run in thread-pool)
        # --------------------------------------------------
        def _audio_dl():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return ydl.prepare_filename(info).replace(info["ext"], "mp3")

        def _video_dl():
            ydl_opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return ydl.prepare_filename(info)

        # --------------------------------------------------
        # 1. Fast path: external API for audio
        # --------------------------------------------------
        if songaudio or (not video and not songvideo):
            file = await download_song(link)
            if file:
                return file, True  # direct download

        # --------------------------------------------------
        # 2. Video download with size check
        # --------------------------------------------------
        if video:
            direct = False
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--cookies",
                cookie_txt_file(),
                "-g",
                "-f",
                "best[height<=?720][width<=?1280]",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                return stdout.decode().splitlines()[0], False  # direct stream URL

            # Fallback to local download after size check
            size = await check_file_size(link)
            if size is None:
                logger.error("Could not determine video file size")
                return None, True
            if size / (1024 * 1024) > 250:
                logger.error("Video too large: %.2f MB", size / (1024 * 1024))
                return None, True

            file_path = await loop.run_in_executor(None, _video_dl)
            return file_path, True

        # --------------------------------------------------
        # 3. Audio fallback via yt-dlp (thread-pool)
        # --------------------------------------------------
        file_path = await loop.run_in_executor(None, _audio_dl)
        return file_path, True
