from ERAVIBES import app  # ERAVIBES module se app object import karen
from pyrogram import filters
import requests

# Sugoi API endpoint
SUGOI_API_URL = "https://sugoi-api.vercel.app/chat"

# Sweet phrases aur emojis
SWEET_PHRASES = [
    "Haan ji, ", "Aap bataiye na, ", "Zaroor, ", "Aapka din acha ho, ", "Mujhe sunke acha laga, ", 
    "Aapki baatein sunkar dil khush ho gaya, ", "Aapki baatein bahut pasand aati hain, "
]
SWEET_EMOJIS = ["😊", "🥰", "💖", "🌸", "🌺", "💫"]

# Random sweet phrase aur emoji choose karein
import random
def make_sweet_reply(response):
    sweet_phrase = random.choice(SWEET_PHRASES)
    sweet_emoji = random.choice(SWEET_EMOJIS)
    return f"{sweet_phrase}{response} {sweet_emoji}"

# Message handler (sirf private messages ke liye)
@app.on_message(filters.private & filters.text)
def handle_message(client, message):
    user_message = message.text

    # Sugoi API ko call karein
    response = requests.get(f"{SUGOI_API_URL}?msg={user_message}")
    
    if response.status_code == 200:
        # JSON response ko parse karein
        json_response = response.json()
        
        # "response" field ko extract karein
        ai_response = json_response.get("response", "Mujhe samajh nahi aaya.")
        
        # Response ko sweet banayein
        sweet_response = make_sweet_reply(ai_response)
        
        # User ko reply karein
        message.reply_text(sweet_response)
    else:
        message.reply_text("Mujhe kuch samajh nahi aaya. Kya aap dobara try kar sakte hain? 😊")
