import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app

# System prompt for high-quality responses
SYSTEM_PROMPT = (
    "You are a helpful and witty AI assistant. Provide concise, engaging, and accurate responses. "
    "If the question is unclear, ask for clarification. Keep responses friendly and professional."
)

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(_: Client, message: Message):
    # Ignore commands and non-replies in groups
    if message.chat.type != ChatType.PRIVATE:
        if not (message.reply_to_message and message.reply_to_message.from_user.id == (await app.get_me()).id):
            return
        if message.text.startswith(("/", "!", "?", ".")):
            return

    try:
        # Prepend system prompt to the user's message
        user_message = f"{SYSTEM_PROMPT}\n\nUser: {message.text}"

        # Try the primary API
        api_url = f"https://sugoi-api.vercel.app/chat?msg={user_message}"
        response = requests.get(api_url)

        if response.status_code == 200:
            await message.reply_text(response.json()['response'])
        else:
            # Fallback API if the primary API fails
            fallback_api_url = f"https://api.affiliateplus.xyz/api/chatbot?message={user_message}&botname=YourBotName"
            fallback_response = requests.get(fallback_api_url)

            if fallback_response.status_code == 200:
                await message.reply_text(fallback_response.json()['message'])
            else:
                await message.reply_text("ChatBot Error: Unable to process your request. Please try again later.")
    except Exception as e:
        await message.reply_text(f"ChatBot Error: {e}")
