import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(_: Client, message: Message):
    # Ignore commands and non-replies in groups
    if message.chat.type != ChatType.PRIVATE:
        if not (message.reply_to_message and message.reply_to_message.from_user.id == (await app.get_me()).id):
            return
        if message.text.startswith(("/", "!", "?", ".")):
            return

    try:
        # System prompt for high-quality responses
        system_prompt = (
            "You are a helpful and witty AI assistant. Provide concise, engaging, and accurate responses. "
            "If the question is unclear, ask for clarification. Keep responses friendly and professional."
        )
        payload = {
            "message": message.text,
            "system_prompt": system_prompt
        }
        response = requests.post("https://sugoi-api.vercel.app/chat", json=payload)

        if response.status_code == 200:
            await message.reply_text(response.json()['response'])
        else:
            await message.reply_text(f"ChatBot Error: {response.status_code} - {response.text}")
    except Exception as e:
        await message.reply_text(f"ChatBot Error: {e}")
