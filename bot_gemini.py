import os
import time
import telebot
from google import genai

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8488063799:AAHWR6zTlfr61WxLO2G3rg3bF8IbjZ2SEz0")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBOBcl43s3kzwWUz1u9HUOYSYuBg0EYkuo")

# Inisialisasi Gemini Client (Library Terbaru)
client = genai.Client(api_key=GEMINI_KEY)
MODEL_ID = "gemini-2.5-flash" # Berdasarkan log Anda, model ini tersedia

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"✅ Bot Gemini 2.5 Flash Aktif!\nKirim teks, foto, atau PDF.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'): return
    try:
        sent_msg = bot.reply_to(message, "Berpikir... ⏳")
        response = client.models.generate_content(model=MODEL_ID, contents=message.text)
        bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    try:
        sent_msg = bot.reply_to(message, "Menganalisis file... ⏳")
        
        # Download file
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            mime_type = "image/jpeg"
        elif message.document and message.document.mime_type == 'application/pdf':
            file_id = message.document.file_id
            mime_type = "application/pdf"
        else:
            bot.edit_message_text("❌ Kirim Foto/PDF.", message.chat.id, sent_msg.message_id)
            return

        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        # Kirim ke Gemini menggunakan library baru
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                message.caption if message.caption else "Apa isi file ini?",
                {"mime_type": mime_type, "data": file_bytes}
            ]
        )
        
        bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Gagal: {str(e)}")

# Hapus Webhook lama jika ada (untuk mencegah error 409)
bot.remove_webhook()
time.sleep(1)

print(f"Bot running with {MODEL_ID}...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)