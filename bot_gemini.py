import os
import telebot
import requests
import base64

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(text, image_data=None, mime_type=None):
    # KUNCI: Kita ganti /v1/ menjadi /v1beta/ karena v1 menolak akunmu
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    if image_data:
        # Jika ada gambar (untuk foto/PDF)
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        payload = {
            "contents": [{
                "parts": [
                    {"text": text},
                    {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                ]
            }]
        }
    else:
        # Jika hanya teks
        payload = {
            "contents": [{"parts": [{"text": text}]}]
        }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Error dari Google: {result.get('error', {}).get('message', 'Format tidak didukung')}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot Aktif! Jalur v1beta dipaksa manual. Silakan kirim teks atau gambar.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    jawaban = get_gemini_response(message.text)
    bot.reply_to(message, jawaban)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    sent_msg = bot.reply_to(message, "Menganalisis gambar... 📸")
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    jawaban = get_gemini_response("Jelaskan gambar ini", downloaded_file, "image/jpeg")
    bot.edit_message_text(jawaban, message.chat.id, sent_msg.message_id)

print("Bot standby di v1beta manual...")
bot.infinity_polling()