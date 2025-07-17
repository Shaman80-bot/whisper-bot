
import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    audio_data = requests.get(file_url).content

    with open("audio.ogg", "wb") as f:
        f.write(audio_data)

    files = {
        'file': ('audio.ogg', open('audio.ogg', 'rb')),
    }
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers,
        files=files,
        data={'model': 'whisper-1', 'language': 'ru'}
    )
    if response.status_code == 200:
        result = response.json()['text']
        bot.reply_to(message, f"📝 Расшифровка: {result}")
    else:
        bot.reply_to(message, f"❌ Ошибка: {response.text}")

bot.infinity_polling()
