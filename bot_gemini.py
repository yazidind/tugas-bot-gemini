import os
import telebot
import requests
import base64

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def call_gemini_api(prompt, file_data=None, mime_type=None):
    # Menggunakan model gemini-3-flash sesuai ketersediaan akunmu di 2026
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # Jika ada data file (Gambar atau PDF)
    if file_data:
        encoded_file = base64.b64encode(file_data).decode('utf-8')
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": encoded_file}}
                ]
            }]
        }
    else:
        # Jika hanya teks
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: {str(e)}. Pastikan file tidak terlalu besar."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot Gemini 3 Flash Aktif!\n\nSaya bisa membantu kamu dengan:\n1. 💬 Tanya Jawab Teks\n2. 🖼️ Analisis Gambar\n3. 📄 Ringkas File PDF")

# Handler untuk Teks
@bot.message_handler(content_types=['text'])
def handle_text(message):
    jawaban = call_gemini_api(message.text)
    bot.reply_to(message, jawaban)

# Handler untuk Gambar & PDF
@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    try:
        sent_msg = bot.reply_to(message, "Sedang memproses... ⏳")
        
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            mime_type = "image/jpeg"
            prompt = "Tolong jelaskan isi gambar ini dengan detail."
        elif message.document and message.document.mime_type == 'application/pdf':
            file_id = message.document.file_id
            mime_type = "application/pdf"
            prompt = "Tolong ringkas isi dokumen PDF ini."
        else:
            bot.edit_message_text("Maaf, kirim foto atau PDF saja.", message.chat.id, sent_msg.message_id)
            return

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        jawaban = call_gemini_api(prompt, downloaded_file, mime_type)
        bot.edit_message_text(jawaban, message.chat.id, sent_msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"Gagal memproses file: {e}")

print("Bot Full Features Gemini 3 Flash is Running...")
bot.infinity_polling()