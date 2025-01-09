import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app
from deep_translator import GoogleTranslator, single_detection

# Initialize translator
translator = GoogleTranslator()

# Define a function to detect language
def detect_language(text):
    try:
        return single_detection(text, api_key=None)
    except:
        return 'en'  # Default to English if detection fails

# Define a function to translate text
def translate_text(text, src_lang, dest_lang):
    try:
        return translator.translate(text, src=src_lang, dest=dest_lang)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(client: Client, message: Message):
    # Ignore non-private chats unless the message is a reply to the bot
    if message.chat.type != ChatType.PRIVATE:
        if not message.reply_to_message:
            return
        if message.reply_to_message.from_user.id != (await client.get_me()).id:
            return
        if message.text and message.text[0] in ["/", "!", "?", "."]:
            return

    try:
        # Detect user message language
        user_lang = detect_language(message.text)
        
        # Translate user message to English
        if user_lang != 'en':
            input_text = translate_text(message.text, user_lang, 'en')
        else:
            input_text = message.text
        
        # Make API request with translated input
        api_url = f"https://chatwithai.codesearch.workers.dev/?chat={input_text}"
        response = requests.get(api_url)
        
        # Check API response status code
        if response.status_code == 200:
            try:
                # Attempt to parse JSON response
                data = response.json()
                # Check if 'response' key exists in the response
                if 'response' in data:
                    api_response = data['response']
                    
                    # Translate API response back to user's language
                    if user_lang != 'en':
                        api_response = translate_text(api_response, 'en', user_lang)
                    
                    await message.reply_text(api_response)
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
