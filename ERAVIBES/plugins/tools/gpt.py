import openai
from pyrogram import filters
from pyrogram.enums import ChatAction
from ERAVIBES import app
import config

# Set up OpenAI API key dynamically
openai.api_key = config.GPT_API

# Command handler
@app.on_message(filters.command(["uru", "duru"], prefixes=["d", "D"]))
async def chat_arvis(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        # Get user query
        query = message.text.split(' ', 1)[1] if len(message.command) > 1 else "Hi!"
        
        # New OpenAI Chat API Call
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change this to "gpt-4" if you want
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},  # Optional system prompt
                {"role": "user", "content": query}
            ],
            temperature=0.2
        )
        
        # Get response
        response = resp.choices[0].message.content
        await message.reply_text(response)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
