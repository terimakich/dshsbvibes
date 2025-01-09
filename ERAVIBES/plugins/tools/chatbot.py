import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(_: Client, message: Message):
    print("Chatbot handler triggered!")  # Debugging line

    # Check if the message is in a group and is a reply to the bot
    if message.chat.type != ChatType.PRIVATE:
        print("Not a private chat, checking conditions...")  # Debugging line
        if not message.reply_to_message:
            print("Not a reply, ignoring...")  # Debugging line
            return
        if message.reply_to_message.from_user.id != (await app.get_me()).id:
            print("Not a reply to the bot, ignoring...")  # Debugging line
            return
        if message.text and message.text[0] in ["/", "!", "?", "."]:
            print("Message starts with a command prefix, ignoring...")  # Debugging line
            return

    print("Processing message...")  # Debugging line

    try:
        # Fetch response from the chatbot API
        api_url = f"https://sugoi-api.vercel.app/chat?msg={message.text}"
        print(f"Calling API: {api_url}")  # Debugging line
        response = requests.get(api_url)
        print(f"API response status code: {response.status_code}")  # Debugging line

        if response.status_code == 200:
            data = response.json()['response']
            print(f"API response data: {data}")  # Debugging line
            await message.reply_text(data)
        elif response.status_code == 429:
            await message.reply_text("ChatBot Error: Too many requests. Please wait a few moments.")
        elif response.status_code >= 500:
            await message.reply_text("ChatBot Error: API server error. Contact us at @CodeSearchDev.")
        else:
            await message.reply_text("ChatBot Error: Unknown Error Occurred. Contact us at @CodeSearchDev.")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")  # Debugging line
        await message.reply_text(f"ChatBot Error: Network error occurred. {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debugging line
        await message.reply_text(f"ChatBot Error: Unexpected error occurred. {e}")
