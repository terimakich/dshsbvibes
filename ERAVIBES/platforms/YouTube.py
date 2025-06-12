import asyncio
import os
import re
import json
import aiohttp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from ERAVIBES.utils.formatters import time_to_seconds
from typing import Union

async def _download_from_maybechiku_api(link: str, file_extension: str, vid_id: str = None):
    maybechiku_base_url = "https://youtube.maybechiku.workers.dev/"
    query_string = {"url": link}

    if not vid_id:
        match = re.search(r'(?:youtu\.be\/|youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})', link)
        if match:
            vid_id = match.group(1)
        else:
            vid_id = "unknown_id_" + str(hash(link))[:8]

    file_path = os.path.join("downloads", f"{vid_id}.{file_extension}")

    if os.path.exists(file_path):
        print(f"DEBUG: File already exists: {file_path}. Skipping download.")
        return file_path, True

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(maybechiku_base_url, params=query_string) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get('success') and data.get('data') and data['data'].get('downloadURL'):
                    download_url = data['data']['downloadURL']
                    print(f"DEBUG: Maybechiku API returned download URL: {download_url}")
                    
                    async with session.get(download_url) as file_response:
                        file_response.raise_for_status()
                        
                        os.makedirs("downloads", exist_ok=True)
                        
                        with open(file_path, "wb") as f:
                            while True:
                                chunk = await file_response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        print(f"DEBUG: Successfully downloaded via Maybechiku API to: {file_path}")
                        return file_path, True
                else:
                    print(f"ERROR: Maybechiku API reports failure or missing downloadURL for {link}: {data}")
                    return None, False
        except aiohttp.ClientError as e:
            print(f"ERROR: Maybechiku API AIOHTTP error for {link}: {e}")
            return None, False
        except json.JSONDecodeError as e:
            print(f"ERROR: Maybechiku API JSON decode error for {link}: {e}. Response was not valid JSON.")
            return None, False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred with Maybechiku API for {link}: {e}")
            return None, False


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + videoid
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
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
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        
        if not results_dict["result"]:
            print(f"WARNING: No search results found for link: {link}")
            return None, None, None, None, None

        result = results_dict["result"][0]
        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]
        duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> Union[str, None]:
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["title"]
        return None

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> Union[str, None]:
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["duration"]
        return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> Union[str, None]:
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
        return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        
        if not results_dict["result"]:
            print(f"WARNING: No track results found for link: {link}")
            return None, None

        result = results_dict["result"][0]
        track_details = {
            "title": result["title"],
            "link": result["link"],
            "vidid": result["id"],
            "duration_min": result["duration"],
            "thumb": result["thumbnails"][0]["url"].split("?")[0],
        }
        return track_details, result["id"]

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        
        a = VideosSearch(link, limit=10)
        results_dict = await a.next()
        result = results_dict.get("result")
        
        if not result or query_type >= len(result) or query_type < 0:
            print(f"WARNING: Invalid query_type ({query_type}) or no results for link: {link}")
            return None, None, None, None

        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(self, link: str, mystic, videoid: Union[bool, str] = None):
        
        if mystic is None:
            print(f"ERROR: 'mystic' (chat_id) is None for link: {link} or videoid: {videoid}. Cannot proceed with download or send message downstream.")
            return None, False

        if videoid:
            full_link = self.base + videoid
        else:
            full_link = link
        
        downloaded_file = None
        direct = False

        file_ext = "mp4"

        print(f"INFO: Attempting download of {full_link} via Maybechiku API...")
        downloaded_file, direct = await _download_from_maybechiku_api(full_link, file_ext, videoid)
        
        if not downloaded_file:
            print(f"ERROR: Maybechiku API failed for {full_link}. No fallback (yt-dlp has been removed).")
            return None, False

        print(f"FINAL DOWNLOAD STATUS: Download completed for link: {full_link} at {downloaded_file}")
        return downloaded_file, direct
