import telebot
import google.generativeai as genai

# --- KONFIGURASI ---
TELEGRAM_TOKEN = "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28"
GEMINI_KEY = "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE"

genai.configure(api_key=GEMINI_KEY)

# Kita coba gunakan 'gemini-pro' jika '1.5-flash' bermasalah di lokal
try:
    model = genai.GenerativeModel('gemini-pro') 
    print("Menggunakan model gemini-pro")
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Tambahkan instruksi ini untuk mengecek apakah model merespon
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Info: Pastikan API Key di Google AI Studio sudah aktif untuk model ini.\nError: {e}")

bot.infinity_polling()