import os
import telebot
import requests

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(text):
    # Kita menembak langsung ke API v1 (Stable) melalui URL
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    # Ambil teks dari struktur JSON Google
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return f"Waduh, Google bilang: {result.get('error', {}).get('message', 'Ada masalah koneksi.')}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot Aktif! Saya menggunakan jalur API langsung agar lebih stabil. Silakan tanya apa saja.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Panggil fungsi API manual
        jawaban = get_gemini_response(message.text)
        bot.reply_to(message, jawaban)
    except Exception as e:
        bot.reply_to(message, f"Gagal: {e}")

print("Bot dijalankan dengan metode Direct API...")
bot.infinity_polling()