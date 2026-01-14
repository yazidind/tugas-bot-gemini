import os
import telebot
import google.generativeai as genai

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

# Inisialisasi Gemini
genai.configure(api_key=GEMINI_KEY)

# Fungsi untuk memilih model yang tersedia
def get_model():
    # Daftar model dari yang paling canggih ke yang paling stabil
    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
    
    for name in model_names:
        try:
            m = genai.GenerativeModel(name)
            # Test kecil untuk memastikan model bisa dipanggil
            return m
        except:
            continue
    return genai.GenerativeModel('gemini-pro') # Last resort

model = get_model()
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"✅ Bot Aktif menggunakan model: {model.model_name}\n\nKirim teks, foto, atau PDF.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'): return
    
    try:
        sent_msg = bot.reply_to(message, "Berpikir... ⏳")
        # Menggunakan generate_content secara langsung
        response = model.generate_content(message.text)
        
        if len(response.text) > 4000:
            bot.send_message(message.chat.id, response.text[:4000])
        else:
            bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Error API: {str(e)}\nCoba lagi nanti.")

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    try:
        sent_msg = bot.reply_to(message, "Menganalisis file... ⏳")
        
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            mime_type = "image/jpeg"
            prompt = message.caption if message.caption else "Jelaskan gambar ini."
        elif message.document and message.document.mime_type == 'application/pdf':
            file_id = message.document.file_id
            mime_type = "application/pdf"
            prompt = message.caption if message.caption else "Ringkas dokumen ini."
        else:
            bot.edit_message_text("❌ Gunakan Foto atau PDF.", message.chat.id, sent_msg.message_id)
            return

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Kirim ke Gemini
        response = model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': downloaded_file}
        ])

        bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Gagal: {str(e)}")

print(f"Bot berjalan dengan model: {model.model_name}")
bot.infinity_polling()