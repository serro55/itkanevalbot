import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

student_messages = {}
student_answers = {}

# 🌿 Başlangıç
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 Hoş geldiniz!\n\n"
        "🎙️ Lütfen Fetih Suresi 29. ayeti ses kaydı olarak gönderiniz.\n\n"
        "📌 İTKAN | Kur’an Akademisi"
    )

# 🎤 Ses alma
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice.file_id

    sent = await context.bot.send_voice(
        chat_id=GROUP_ID,
        voice=voice
    )

    student_messages[sent.message_id] = user.id

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"""🎧 Yeni tilavet

👤 Öğrenci: {user.first_name}
🆔 ID: {user.id}

📌 İTKAN"""
    )

    keyboard = [
        [InlineKeyboardButton("⭐ Değerlendir", callback_data=f"rate_{sent.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    keyboard2 = [
        [InlineKeyboardButton("✅ Evet", callback_data="tajweed_yes")],
        [InlineKeyboardButton("❌ Hayır", callback_data="tajweed_no")]
    ]

    await update.message.reply_text(
        "📌 Tecvid eğitimi aldınız mı?",
        reply_markup=InlineKeyboardMarkup(keyboard2)
    )

# 👩‍🎓 Tecvid cevabı
async def handle_tajweed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    student_answers[query.from_user.id] = "Aldı" if query.data == "tajweed_yes" else "Almadı"

    await query.message.reply_text("✅ Cevabınız kaydedildi.")

# ⭐ Değerlendirme aç
async def handle_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])

    keyboard = [
        [InlineKeyboardButton("🔵📖 Kaide-i Nuraniyye", callback_data=f"level_nurani_{message_id}")],
        [InlineKeyboardButton("🟡 Başlangıç", callback_data=f"level_beginner_{message_id}")],
        [InlineKeyboardButton("🟠 Orta Seviye", callback_data=f"level_intermediate_{message_id}")],
        [InlineKeyboardButton("🔴 İleri Seviye", callback_data=f"level_advanced_{message_id}")]
    ]

    await query.message.reply_text(
        "📊 Seviye seçiniz:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📊 Seviye değerlendirme
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, level, message_id = query.data.split("_")
    message_id = int(message_id)

    student_id = student_messages.get(message_id)

    if not student_id:
        await query.message.reply_text("❌ Öğrenci bulunamadı.")
        return

    tajweed = student_answers.get(student_id, "Bilinmiyor")

    level_map = {
        "nurani": "🔵📖 Kaide-i Nuraniyye",
        "beginner": "🟡 Başlangıç",
        "intermediate": "🟠 Orta Seviye",
        "advanced": "🔴 İleri Seviye"
    }

    advice_map = {
        "nurani": "📌 Harfleri öğrenmeye odaklan\n🎧 Günlük dinleme yap\n👩‍🏫 Nuraniyye derslerine katıl",
        "beginner": "📌 Temel tecvid çalış\n🎧 Günlük سماعي ختمة yap\n👩‍🏫 Başlangıç derslerine devam et",
        "intermediate": "📌 Med ve gunne kurallarına dikkat et\n🎧 سماعي ختمة yap\n👩‍🏫 Orta seviye derslerini takip et",
        "advanced": "📌 İleri seviye detaylara odaklan\n🎧 Uzun dinleme yap\n👩‍🏫 İleri derslerle devam et"
    }

    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Değerlendirmeniz:

{level_map[level]}

Tecvid durumu: {tajweed}

{advice_map[level]}

🎧 Öneri:
• Şeyh Ayman Suwaid tilavetini dinleyiniz
• Sadece dinleme üzerine سماعي ختمة yapınız

🌿 İTKAN ile devam ediniz"""
    )

    await query.message.reply_text("✅ Gönderildi")

# 💬 Grup cevapları
async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.chat.id != GROUP_ID:
        return

    if not message.reply_to_message:
        return

    replied_id = message.reply_to_message.message_id

    student_id = student_messages.get(replied_id)

    if not student_id:
        return

    if not message.text:
        return

    await context.bot.send_message(
        chat_id=student_id,
        text=f"📊 Değerlendirmeniz:\n\n{message.text}\n\n📌 İTKAN"
    )

# ▶️ Çalıştır
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CallbackQueryHandler(handle_tajweed, pattern="^tajweed_"))
app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), handle_group_reply))

app.run_polling()
