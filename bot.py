import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

student_messages = {}
student_answers = {}

NAME, AGE = range(2)

# 🌿 تسجيل
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧕🏻 İsminizi & soyjsminizi yazınız:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🪻 Yaşınızı yazınız:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    await update.message.reply_text(
        "🎧 Lütfen Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz."
    )
    return ConversationHandler.END

# 🎤 استقبال الصوت
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice.file_id

    name = context.user_data.get("name", "Bilinmiyor")
    age = context.user_data.get("age", "Bilinmiyor")

    sent = await context.bot.send_voice(chat_id=GROUP_ID, voice=voice)

    student_messages[sent.message_id] = user.id

    keyboard = [
        [InlineKeyboardButton("⭐ Değerlendir", callback_data=f"rate_{sent.message_id}")],
        [InlineKeyboardButton("⚠️ Tekrar gönder", callback_data=f"return_{sent.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"👤 {name} ({age})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ⭐ التقييم
async def handle_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])

    keyboard = [
        [InlineKeyboardButton("🔵📖 Kaide-i Nuraniyye (Başlangıç öncesi)", callback_data=f"level_nurani_{message_id}"),
        [InlineKeyboardButton("🟡 Başlangıç", callback_data=f"level_beginner_{message_id}")],
        [InlineKeyboardButton("🟠 Orta Seviye", callback_data=f"level_intermediate_{message_id}")],
        [InlineKeyboardButton("🔴 İleri Seviye", callback_data=f"level_advanced_{message_id}")]
    ]

    await query.message.reply_text(
        "📊 Seviye seçiniz:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📊 تحديد المستوى
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, level, message_id = query.data.split("_")
    message_id = int(message_id)

    student_id = student_messages.get(message_id)
    if not student_id:
        return

    levels = {
        "nurani": "🔵📖 Kaide-i Nuraniyye",
        "beginner": "🟡 Başlangıç",
        "intermediate": "🟠 Orta Seviye",
        "advanced": "🔴 İleri Seviye"
    }

    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Seviye: {levels[level]}

📌 Gelişim kaydınız oluşturulmuştur.

🤲 Allah bize Kur’an’ı Resûlullah (s.a.v) gibi okumayı nasip etsin."""
    )

# ⚠️ إعادة الإرسال + تذكير بالآية
async def handle_return(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])
    student_id = student_messages.get(message_id)

    if not student_id:
        return

    await context.bot.send_message(
        chat_id=student_id,
        text="""⚠️ Lütfen dikkat

📖 Sizden istenen ayet: Fetih Suresi 29. ayet

🎧 Lütfen bu ayeti tekrar ses kaydı olarak gönderiniz.

🤲 Allah yardımcınız olsun."""
    )

    await query.message.reply_text("🔁 Öğrenciye geri gönderildi.")

# 👩‍🏫 لوحة المعلمة
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("📊 Panel", callback_data="admin")]
    ]

    await update.message.reply_text(
        "👩‍🏫 Yönetim Paneli",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 💬 رد المعلمة
async def group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != GROUP_ID:
        return

    if not update.message.reply_to_message:
        return

    student_id = student_messages.get(update.message.reply_to_message.message_id)

    if student_id:
        await context.bot.send_message(
            chat_id=student_id,
            text=f"📊 Değerlendirme:\n\n{update.message.text}"
        )

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
    },
    fallbacks=[]
)

app.add_handler(conv)
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), group_reply))

app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))

app.run_polling()
