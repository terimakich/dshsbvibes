import os
import requests
from typing import Optional
from pathlib import Path
from ..logging import LOGGER

def download_and_save_content(url: str, save_path: str = "cookies/cookies.txt") -> Optional[str]:
    try:
        # Ensure the directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Write the content to the file
        with open(save_path, "w") as file:
            file.write(response.text)

        return save_path

    except requests.exceptions.RequestException as e:
        LOGGER(__name__).error(f"Failed to download content from {url}: {e}")
    except IOError as e:
        LOGGER(__name__).error(f"Failed to write to file {save_path}: {e}")

    return None

def fetch_and_store_cookies(cookie_url: str) -> None:
    try:
        # Extract the paste ID from the URL
        paste_id = cookie_url.strip().split("/")[-1]
        raw_content_url = f"https://batbin.me/raw/{paste_id}"

        # Download and save the content
        file_path = download_and_save_content(raw_content_url)
        if file_path and os.path.getsize(file_path) > 0:
            LOGGER(__name__).info(f"Cookies saved successfully to {file_path}.")
        else:
            LOGGER(__name__).error("Failed to save cookies or the file is empty. 🥹")

    except Exception as e:
        LOGGER(__name__).error(f"An unexpected error occurred while saving cookies: {e}")
