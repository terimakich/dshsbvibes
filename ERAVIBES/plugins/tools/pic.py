import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from ERAVIBES import app


# Function to fetch image URLs from Google Images
def fetch_google_images(query, num_images=7):
    url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [img['src'] for img in BeautifulSoup(response.text, 'html.parser').find_all('img', {'src': True})[:num_images]]
    return []

# /pic command handler
@app.on_message(filters.command("pic"))
def send_images(client, message):
    query = message.text.split("/pic ", 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        message.reply_text("Usage: /pic <query>")
        return

    image_urls = fetch_google_images(query, num_images=7)
    if not image_urls:
        message.reply_text("No images found.")
        return

    for url in image_urls:
        try:
            message.reply_photo(url)
        except Exception as e:
            print(f"Error sending image: {e}")
