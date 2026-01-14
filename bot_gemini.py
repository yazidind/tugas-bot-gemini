import os
import telebot
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# --- KONFIGURASI ---
# Menggunakan os.getenv agar aman di Cloud, tapi tetap ada backup tokenmu
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

genai.configure(api_key=GEMINI_KEY)

# Paksa menggunakan gemini-1.5-flash karena ini yang paling stabil untuk API gratis saat ini
model = genai.GenerativeModel('gemini-1.5-flash')

# KUNCI UTAMA: Memaksa versi API ke 'v1' untuk menghindari error 404 v1beta
request_config = RequestOptions(api_version="v1")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot Gemini 1.5 Flash siap digunakan! Kirimkan pertanyaanmu.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Menambahkan request_options=request_config agar tidak error 404
        response = model.generate_content(message.text, request_options=request_config)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {e}")

print("Bot sedang berjalan...")
bot.infinity_polling()