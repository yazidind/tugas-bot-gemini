import os
import telebot
import google.generativeai as genai

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

# Inisialisasi Gemini
genai.configure(api_key=GEMINI_KEY)

# Menggunakan Gemini 1.5 Flash (Sangat cepat dan mendukung Gambar/PDF)
# Jika masih error, ganti ke 'gemini-1.5-pro' atau 'gemini-1.0-pro'
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot Gemini 1.5 Aktif!\n\nKirimkan teks, foto, atau file PDF untuk dianalisis.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'): return
    
    try:
        sent_msg = bot.reply_to(message, "Berpikir... ⏳")
        response = model.generate_content(message.text)
        
        # Kirim jawaban (potong jika terlalu panjang untuk Telegram)
        if len(response.text) > 4000:
            bot.send_message(message.chat.id, response.text[:4000])
        else:
            bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan: {str(e)}")

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    try:
        sent_msg = bot.reply_to(message, "Sedang memproses file... ⏳")
        
        # Tentukan file_id dan MIME type
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            mime_type = "image/jpeg"
            prompt = message.caption if message.caption else "Jelaskan isi gambar ini."
        elif message.document and message.document.mime_type == 'application/pdf':
            file_id = message.document.file_id
            mime_type = "application/pdf"
            prompt = message.caption if message.caption else "Ringkas isi PDF ini."
        else:
            bot.edit_message_text("❌ Maaf, hanya mendukung Foto atau PDF.", message.chat.id, sent_msg.message_id)
            return

        # Download file dari Telegram
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Kirim ke Gemini menggunakan format dictionary untuk file
        response = model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': downloaded_file}
        ])

        if len(response.text) > 4000:
            bot.send_message(message.chat.id, response.text[:4000])
        else:
            bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Gagal memproses: {str(e)}")

print("Bot Gemini 1.5 Flash sedang berjalan...")
bot.infinity_polling()