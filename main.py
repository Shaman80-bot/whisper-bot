import telebot
import requests
import os
from flask import Flask
import threading

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("audio.ogg", "wb") as f:
        f.write(downloaded_file)

    files = {
        'file': ('audio.ogg', open('audio.ogg', 'rb')),
    }
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    data = {
        'model': 'whisper-1',
        'language': 'ru'
    }

    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code == 200:
        result = response.json()['text']
        bot.reply_to(message, f"📄 Расшифровка:\n{result}")
    else:
        bot.reply_to(message, f"❌ Ошибка: {response.text}")

def start_bot():
    bot.infinity_polling()

threading.Thread(target=start_bot).start()

app = Flask(__name__)

@app.route('/')
def home():
    return 'Whisper bot is running!'

port = int(os.environ.get('PORT', 10000))
app.run(host='0.0.0.0', port=port)
