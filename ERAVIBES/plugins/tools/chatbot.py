import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app

# Define a function to preprocess user input
def preprocess_input(input_text):
    # Remove special characters and convert to lowercase
    input_text = ''.join(e for e in input_text if e.isalnum() or e.isspace()).lower()
    return input_text

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(_: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        if not message.reply_to_message:
            return
        if message.reply_to_message.from_user.id != (await app.get_me()).id:
            return
        if message.text and message.text[0] in ["/", "!", "?", "."]:
            return

    try:
        # Preprocess user input
        input_text = preprocess_input(message.text)
        
        # Make API request with preprocessed input
        response = requests.get("https://sugoi-api.vercel.app/chat?msg=" + input_text)
        
        # Check API response status code
        if response.status_code == 200:
            try:
                # Attempt to parse JSON response
                data = response.json()
                # Check if 'response' key exists in the response
                if 'response' in data:
                    await message.reply_text(data['response'])
                else:
                    await message.reply_text("ChatBot Error: Invalid response from API.")
            except ValueError:
                await message.reply_text("ChatBot Error: Failed to parse API response.")
        elif response.status_code == 429:
            await message.reply_text("ChatBot Error: Too many requests. Please wait a few moments.")
        elif response.status_code >= 500:
            await message.reply_text("ChatBot Error: API server error. Contact us at @net_pro_max.")
        else:
            await message.reply_text("ChatBot Error: Unknown Error Occurred. Contact us at @net_pro_max.")
    except requests.exceptions.RequestException as e:
        await message.reply_text(f"ChatBot Error: Network error occurred. {e}")
