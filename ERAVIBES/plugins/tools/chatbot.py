import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app

SYSTEM_PROMPT = "Act as an AI assistant capable of providing helpful, engaging, and accurate responses. Use conversational language and maintain a polite and friendly tone. If you don't understand the input, ask for clarification instead of guessing."

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(_: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE and (
        not message.reply_to_message or 
        message.reply_to_message.from_user.id != (await app.get_me()).id or 
        message.text[0] in ["/", "!", "?", "."]
    ):
        return

    try:
        # Append SYSTEM_PROMPT to the user's message
        prompt_message = SYSTEM_PROMPT + "\n" + message.text
        response = requests.get(f"https://sugoi-api.vercel.app/chat?msg={prompt_message}")
        
        if response.ok:
            await message.reply_text(response.json().get('response', "Error: Invalid response from API."))
        else:
            error_message = (
                "Too many requests. Try again later." if response.status_code == 429 else 
                "API server error. Contact support @net_pro_max." if response.status_code >= 500 else 
                "Unknown error occurred. Contact support @net_pro_max."
            )
            await message.reply_text(f"ChatBot Error: {error_message}")
    except requests.RequestException as e:
        await message.reply_text(f"ChatBot Error: Network error occurred. {e}")
