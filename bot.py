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

# 🌿 بدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌿 İsminizi yazınız:")
    return NAME

# 👤 اسم
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🪻 Yaşınızı yazınız:")
    return AGE

# 🎂 عمر
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("📝 Bilgileri güncelle", callback_data="update_info")]
    ]

    await update.message.reply_text(
        "🎧 Fetih Suresi 29. ayeti gönderiniz.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ConversationHandler.END

# 🎤 الصوت
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

# ⭐ عرض التقييم
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

# 🎯 النصوص لكل مستوى
levels = {
    "nurani": "🔵📖 Kaide-i Nuraniyye",
    "beginner": "🟡 Başlangıç",
    "intermediate": "🟠 Orta Seviye",
    "advanced": "🔴 İleri Seviye"
}

messages = {
    "nurani": """🌱 Güçlü bir başlangıç yapıyorsunuz.
Başlangıcınızı sağlam kurmanız ilerlemenizi kolaylaştırır.""",

    "beginner": """✨ Başlangıç seviyeniz güzel.
Düzenli çalışma ile daha hızlı ilerleyebilirsiniz.""",

    "intermediate": """📈 İyi bir gelişim içindesiniz.
Daha fazla pratik ile seviye atlayabilirsiniz.""",

    "advanced": """🏆 Mükemmel bir seviye!
Artık öğrendiklerinizi uygulama ve öğretme aşamasındasınız."""
}

# 🎯 التقييم + الرسائل
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, level, message_id = query.data.split("_")
    message_id = int(message_id)

    student_id = student_messages.get(message_id)
    if not student_id:
        return

    text = (
        f"📊 Seviye\n\n"
        f"{levels[level]}\n\n"
        f"{messages[level]}\n\n"
        f"🎯 Hedefinize odaklanın.\n\n"
        f"📌 Kaydınız oluşturulmuştur.\n"
        f"📚 Dersleri takip etmeye devam edin:\n"
        f"https://t.me/itkanakademi"
    )

    await context.bot.send_message(
        chat_id=student_id,
        text=text
    )

    # حذف الأزرار + تأكيد للمعلمة
    await query.edit_message_text(
        text="✅ Değerlendirme gönderildi."
    )

# ⚠️ إعادة التسجيل
async def handle_return(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])
    student_id = student_messages.get(message_id)

    if not student_id:
        return

    await context.bot.send_message(
        chat_id=student_id,
        text="""⚠️ Lütfen Fetih Suresi 29. ayeti tekrar gönderiniz."""
    )

    await query.message.reply_text("🔁 Gönderildi")

# تشغيل البوت
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
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))

app.run_polling()
