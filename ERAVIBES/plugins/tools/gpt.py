import os
import openai
import requests
from pyrogram import filters
from pyrogram.enums import ChatAction
from ERAVIBES import app
import config
from config import GPT_API

# Set up OpenAI API
openai.api_key = config.GPT_API


# Command for GPT chat with user's name
@app.on_message(filters.command(["uru", "duru"], prefixes=["d", "D"]))
async def chat_arvis(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name
        if len(message.command) < 2:
            await message.reply_text(f"**Hello {name}, I am Duru. How can I help you today?**")
        else:
            query = message.text.split(' ', 1)[1]
            MODEL = "gpt-3.5-turbo"
            resp = openai.ChatCompletion.create(model=MODEL, messages=[{"role": "user", "content": query}],
                                                 temperature=0.2)
            response_text = resp['choices'][0]["message"]["content"]
            await message.reply_text(response_text)
    except Exception as e:
        await message.reply_text(f"**Error**: {e}")
