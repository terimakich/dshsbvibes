from pyrogram import Client, filters
import requests
#import base64
#from io import BytesIO
from ERAVIBES import app


# Define the base URL
base_url = "https://chatwithai.codesearch.workers.dev/?chat="

# Function to handle the /ai command
@app.on_message(filters.command("ai"))
def ai_command(client, message):
    # Extract the query from the message
    query = " ".join(message.command[1:])
    
    if not query:
        message.reply_text("Please provide a query after the /ai command.")
        return
    
    # Send the GET request
    response = requests.get(base_url + query)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Send the response back to the user
        message.reply_text(response.text)
    else:
        message.reply_text("Failed to get a response from the AI.")



@app.on_message(filters.command("gen"))
def generate_image(client, message):
    # Extract the query from the message
    if len(message.command) > 1:
        query = " ".join(message.command[1:])
        url = f"https://text2img.codesearch.workers.dev/?prompt={query}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("API Response:", data)  # Print the JSON response for debugging
            
            # Extract the image URL or handle the response
            if "url" in data:
                image_url = data["url"]
                message.reply_text(f"Here is your generated image: {image_url}")
            else:
                message.reply_text("No image URL found in the API response.")
        else:
            message.reply_text("Failed to generate image. Please try again later.")
    else:
        message.reply_text("Please provide a query after the /gen command. Example: /gen cat")
