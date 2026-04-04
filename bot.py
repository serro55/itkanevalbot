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

# ربط الرسائل بالطلاب
student_messages = {}

# 🚀 Başlangıç
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 Hoş geldiniz!\n\n"
        "Kur’an tilavetinizi geliştirme yolunda attığınız bu adım çok kıymetlidir.\n\n"
        "<b>🎙️ Lütfen Fetih Suresi 29. ayeti ses kaydı olarak gönderiniz.</b>\n\n"
        "📌 İTKAN | Kur’an Akademisi",
        parse_mode="HTML"
    )

# 🎤 Ses alma
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice.file_id

    # إرسال للجروب
    sent_message = await context.bot.send_voice(
        chat_id=GROUP_ID,
        voice=voice
    )

    # حفظ الربط
    student_messages[sent_message.message_id] = user.id

    text = f"""🎧 Yeni tilavet gönderildi

👤 Öğrenci: {user.first_name}
🆔 ID: {user.id}

📌 İTKAN | Kur’an Akademisi"""

    await context.bot.send_message(chat_id=GROUP_ID, text=text)

    # زر التقييم
    keyboard = [
        [InlineKeyboardButton("⭐ Değerlendir", callback_data=f"rate_{sent_message.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ⭐ فتح التقييم
async def handle_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])

    keyboard = [
        [InlineKeyboardButton("📖 Kaide-i Nuraniyye", callback_data=f"level_nurani_{message_id}")],
        [InlineKeyboardButton("🟢 Başlangıç", callback_data=f"level_beginner_{message_id}")],
        [InlineKeyboardButton("🟡 Orta", callback_data=f"level_intermediate_{message_id}")],
        [InlineKeyboardButton("🔵 İleri", callback_data=f"level_advanced_{message_id}")]
    ]

    await query.message.reply_text(
        "📊 Seviye seçiniz:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📊 تحليل + إرسال
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, level, message_id = query.data.split("_")
    message_id = int(message_id)

    student_id = student_messages.get(message_id)

    if not student_id:
        await query.message.reply_text("❌ Öğrenci bulunamadı.")
        return

    level_map = {
        "nurani": "📖 Kaide-i Nuraniyye (ön başlangıç)",
        "beginner": "🟢 Başlangıç",
        "intermediate": "🟡 Orta",
        "advanced": "🔵 İleri"
    }

    analysis_map = {
        "nurani": "🔍 Analiz: Harfleri doğru öğrenmek için temel eğitime ihtiyacın var.",
        "beginner": "🔍 Analiz: Temel seviyede ilerliyorsun, telaffuzunu geliştirmeye devam et.",
        "intermediate": "🔍 Analiz: Orta seviyedesin, tecvid kurallarına daha fazla dikkat et.",
        "advanced": "🔍 Analiz: Çok iyi bir seviyedesin, artık detaylara odaklanabilirsin."
    }

    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Değerlendirmeniz:

{level_map[level]}

{analysis_map[level]}

📌 İTKAN | Kur’an Akademisi"""
    )

    await query.message.reply_text("✅ Değerlendirme öğrenciye gönderildi.")

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))

app.run_polling()
