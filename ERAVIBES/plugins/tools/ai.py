from pyrogram import Client, filters
import requests
import base64
from io import BytesIO
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
            print(data)  # Debugging: Print the API response
            
            # Check if the API returns a direct URL
            if "url" in data:
                image_url = data["url"]
                message.reply_photo(image_url)
            
            # Check if the API returns base64 image data
            elif "image" in data:
                image_data = data["image"]
                image_bytes = base64.b64decode(image_data)
                message.reply_photo(BytesIO(image_bytes))
            
            # Check if the API returns binary image data
            elif isinstance(data, bytes):
                message.reply_photo(BytesIO(data))
            
            # Handle unknown response format
            else:
                message.reply_text("Unable to extract image from the API response.")
        else:
            message.reply_text("Failed to generate image. Please try again later.")
    else:
        message.reply_text("Please provide a query after the /gen command. Example: /gen cat")
