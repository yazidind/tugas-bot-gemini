import os
import telebot
import requests
import base64

# --- KONFIGURASI ---
# Sangat disarankan menggunakan os.getenv tanpa hardcode token di script untuk keamanan
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def call_gemini_api(prompt, file_data=None, mime_type=None):
    # Gunakan model gemini-1.5-flash (versi terbaru saat ini)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    
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
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        # Cek jika ada error dari API Gemini
        if 'error' in result:
            return f"API Error: {result['error']['message']}"
            
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: Terjadi kesalahan pada server AI. ({str(e)})"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot Gemini Aktif!\n\nKirimkan teks, foto, atau PDF untuk mulai.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Menghindari bot merespon teks kosong atau perintah
    if message.text.startswith('/'): return
    
    sent_msg = bot.reply_to(message, "Berpikir... ⏳")
    jawaban = call_gemini_api(message.text)
    
    # Telegram limit 4096 karakter, jika lebih harus dipotong
    if len(jawaban) > 4000:
        for i in range(0, len(jawaban), 4000):
            bot.send_message(message.chat.id, jawaban[i:i+4000])
    else:
        bot.edit_message_text(jawaban, message.chat.id, sent_msg.message_id)

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    try:
        sent_msg = bot.reply_to(message, "Sedang menganalisis file... ⏳")
        
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            mime_type = "image/jpeg"
            prompt = message.caption if message.caption else "Jelaskan gambar ini."
        elif message.document and message.document.mime_type == 'application/pdf':
            file_id = message.document.file_id
            mime_type = "application/pdf"
            prompt = message.caption if message.caption else "Ringkas isi PDF ini."
        else:
            bot.edit_message_text("Format tidak didukung. Kirim Foto atau PDF.", message.chat.id, sent_msg.message_id)
            return

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        jawaban = call_gemini_api(prompt, downloaded_file, mime_type)
        
        if len(jawaban) > 4000:
            bot.send_message(message.chat.id, jawaban[:4000])
        else:
            bot.edit_message_text(jawaban, message.chat.id, sent_msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"Gagal memproses file: {e}")

print("Bot is Running...")
bot.infinity_polling()