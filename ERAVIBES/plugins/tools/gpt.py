from pyrogram import filters
import openai
from ERAVIBES import app

# Function to interact with OpenAI GPT
def get_ai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ya jo bhi model aap use kar rahe ho
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Command handler
@app.on_message(filters.command("ask") & filters.private)
def ask_gpt(client, message):
    user_prompt = message.text.split(maxsplit=1)[1]  # User input after /ask
    if not user_prompt:
        message.reply_text("Please provide a prompt!")
        return
    
    ai_response = get_ai_response(user_prompt)
    message.reply_text(ai_response)
