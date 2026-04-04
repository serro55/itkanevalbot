import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

student_answers = {}

# 🎯 بداية البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 Hoş geldiniz!\n\n"
        "Kur’an tilavetinizi geliştirme yolunda attığınız bu adım çok kıymetlidir ✨\n\n"
        "🎙️ Lütfen Fetih Suresi 29. ayeti ses kaydı olarak gönderiniz.\n\n"
        "📌 İTKAN | Kur’an Akademisi"
    )

# 🎤 استقبال الفويس
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice.file_id

    context.user_data["user_id"] = user.id

    text = f"""🎧 Yeni tilavet gönderildi

👤 Öğrenci: {user.first_name}
🆔 ID: {user.id}

📌 İTKAN | Kur’an Akademisi"""

    await context.bot.send_voice(chat_id=GROUP_ID, voice=voice)
    await context.bot.send_message(chat_id=GROUP_ID, text=text)

    # سؤال التجويد
    keyboard = [
        [InlineKeyboardButton("✅ Evet", callback_data="student_yes")],
        [InlineKeyboardButton("❌ Hayır", callback_data="student_no")]
    ]

    await update.message.reply_text(
        "📌 Tecvid eğitimi aldınız mı?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 👩‍🎓 جواب الطالبة
async def handle_student_tajweed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    answer = "Aldı" if query.data == "student_yes" else "Almadı"

    student_answers[user_id] = answer

    await query.message.reply_text(
        "✅ Cevabınız kaydedildi.\n\n"
        "⏳ Değerlendirme süreciniz başlamıştır.\n"
        "Değerlendirmeniz en kısa sürede tarafınıza iletilecektir inşallah 🌿\n\n"
        "📌 İTKAN | Kur’an Akademisi"
    )

# 👩‍🏫 تقييم المعلمة (مستويات)
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    level = data[1]
    student_id = int(data[2])

    level_map = {
        "nurani": "📖 Kaide-i Nuraniyye",
        "beginner": "🟢 Başlangıç",
        "intermediate": "🟡 Orta",
        "advanced": "🔵 İleri"
    }

    tajweed = student_answers.get(student_id, "Bilinmiyor")

    message = f"""📊 Değerlendirmeniz:

Seviye: {level_map.get(level)}
Tecvid: {tajweed}

📌 İTKAN | Kur’an Akademisi"""

    await context.bot.send_message(chat_id=student_id, text=message)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CallbackQueryHandler(handle_student_tajweed, pattern="^student_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))

app.run_polling()
