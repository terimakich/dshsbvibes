import os
import openai
import requests
from pyrogram import filters
from pyrogram.enums import ChatAction
from ERAVIBES import app
import config

# Load OpenAI API Key
openai.api_key = config.GPT_API

# Configuration for multiple APIs
API_CONFIG = {
    "OpenAI": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "headers": {"Authorization": f"Bearer {config.GPT_API}", "Content-Type": "application/json"},
        "method": "POST",
        "payload_template": lambda query: {
            "model": "text-davinci-003",
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.2
        }
    },
    # Example for another API
    "AnotherAPI": {
        "endpoint": "https://another-api.com/v1/generate",
        "headers": {"Authorization": "Bearer YOUR_API_KEY_HERE", "Content-Type": "application/json"},
        "method": "POST",
        "payload_template": lambda query: {"input_text": query, "options": {"temperature": 0.7}}
    }
}

# Function to handle API calls
def call_api(api_name, query):
    """
    Generic function to call any API defined in API_CONFIG.
    """
    if api_name not in API_CONFIG:
        raise ValueError(f"API '{api_name}' is not configured.")
    
    config = API_CONFIG[api_name]
    url = config['endpoint']
    headers = config['headers']
    method = config['method']
    payload = config['payload_template'](query)

    if method == "POST":
        response = requests.post(url, headers=headers, json=payload)
    elif method == "GET":
        response = requests.get(url, headers=headers, params=payload)
    else:
        raise ValueError("Unsupported HTTP method")

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Command for GPT chat with user's name
@app.on_message(filters.command(["uru", "duru"], prefixes=["d", "D"]))
async def chat_arvis(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name
        
        if len(message.command) < 2:
            await message.reply_text(f"Hello {name}, I am Duru. How can I help you today?")
        else:
            query = message.text.split(' ', 1)[1]
            api_name = "OpenAI"  # Replace with dynamic selection logic if needed
            response = call_api(api_name, query)

            if api_name == "OpenAI":
                response_text = response['choices'][0]["message"]["content"]
            elif api_name == "AnotherAPI":
                response_text = response.get("generated_text", "No response text provided.")
            else:
                response_text = "API response not handled."

            await message.reply_text(response_text)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
