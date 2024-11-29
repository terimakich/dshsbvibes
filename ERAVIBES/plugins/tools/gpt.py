import requests
from pyrogram import filters
from pyrogram.enums import ChatAction
from ERAVIBES import app
import config

# GroqCloud API Key
GPT_API = config.GPT_API

# Command handler
@app.on_message(filters.command(["uru", "duru"], prefixes=["d", "D"]))
async def chat_arvis(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        # Get user query
        query = message.text.split(' ', 1)[1] if len(message.command) > 1 else "Hi!"
        
        # GroqCloud API call
        response = requests.post(
            "https://api.groqcloud.com/v1/chat",  # Replace with GroqCloud's actual endpoint
            headers={"Authorization": f"Bearer {GPT_API}", "Content-Type": "application/json"},
            json={"prompt": query, "max_tokens": 150, "temperature": 0.7}
        )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            reply_text = result.get("response", "No response received from API.")
            await message.reply_text(reply_text)
        else:
            await message.reply_text(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
