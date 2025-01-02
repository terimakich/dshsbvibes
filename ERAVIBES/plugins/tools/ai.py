from pyrogram import Client, filters
import requests
from ERAVIBES import app

# Command handler for /gen
@app.on_message(filters.command("gen"))
def generate_image(client, message):
    # Extract the query from the message
    if len(message.command) > 1:
        query = " ".join(message.command[1:])
        url = f"https://text2img.codesearch.workers.dev/?prompt={query}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Assuming the API returns a direct URL to the image
            image_url = data.get("url", "No URL found in response")
            message.reply_text(f"Here is your generated image: {image_url}")
        else:
            message.reply_text("Failed to generate image. Please try again later.")
    else:
        message.reply_text("Please provide a query after the /gen command. Example: /gen cat")
