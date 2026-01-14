import os
import telebot
import google.generativeai as genai

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8248342383:AAHqfK3TqX4U_BL_AHUAY3TO0emLRoObj28")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyBwjPptatnfsIYEQuPE_Be7bxgDnn-2WbE")

genai.configure(api_key=GEMINI_KEY)

# --- FUNGSI DIAGNOSIS MODEL ---
def find_best_model():
    print("Mengecek daftar model yang tersedia...")
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Model ditemukan: {available_models}")
        
        # Urutan prioritas model
        priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']
        
        for p in priorities:
            if p in available_models:
                print(f"Menggunakan model terbaik: {p}")
                return p
        
        if available_models:
            print(f"Menggunakan model alternatif: {available_models[0]}")
            return available_models[0]
    except Exception as e:
        print(f"Gagal list_models: {e}")
    
    # Fallback jika list_models gagal
    return 'gemini-1.5-flash'

# Inisialisasi Model
SELECTED_MODEL_NAME = find_best_model()
model = genai.GenerativeModel(SELECTED_MODEL_NAME)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"✅ Bot Aktif!\nModel: {SELECTED_MODEL_NAME}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'): return
    try:
        # Gunakan stream=False untuk kestabilan awal
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    try:
        sent_msg = bot.reply_to(message, "⏳ Memproses...")
        
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
        data = bot.download_file(file_info.file_path)

        response = model.generate_content([
            message.caption if message.caption else "Analisis ini",
            {'mime_type': mime_type, 'data': data}
        ])
        
        bot.edit_message_text(response.text, message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Gagal: {str(e)}")

print(f"Bot running with {SELECTED_MODEL_NAME}...")
bot.infinity_polling()