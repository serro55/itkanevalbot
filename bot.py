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

student_messages = {}

NAME, AGE = range(2)

# 🌿 البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌿 Hoş geldiniz")
    await update.message.reply_text("👤 İsminizi yazınız:")
    return NAME

# 👤 الاسم
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🪻 Yaşınızı yazınız:")
    return AGE

# 🪻 العمر
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    await update.message.reply_text(
        "🎧 Lütfen Fetih Suresi 29. ayeti ses kaydı olarak gönderiniz."
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
        [InlineKeyboardButton("⚠️ Ayet tekrar iste", callback_data=f"return_{sent.message_id}")],
        [InlineKeyboardButton("📝 İsim & yaş iste", callback_data=f"info_{sent.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"👤 {name} ({age})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ⭐ عرض المستويات
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

# 🎯 رسائل المستويات
levels = {
    "nurani": "🔵📖 Kaide-i Nuraniyye",
    "beginner": "🟡 Başlangıç",
    "intermediate": "🟠 Orta Seviye",
    "advanced": "🔴 İleri Seviye"
}

messages = {
    "nurani": """🌱 Güçlü bir başlangıç yapıyorsunuz.
Sağlam temel sizi ileri taşır.""",

    "beginner": """🎉Güzel bir başlangıç yaptınız.
Düzenli çalışma sizi orta seviyeye ulaştırır.""",

    "intermediate": """📈 İyi bir seviyedesiniz.
Daha fazla pratik ile ileri seviyeye geçebilirsiniz.""",

    "advanced": """🏆 Çok güzel bir seviyedesiniz.

Öğrendikleriniz bir emanettir, uygulamanız gerekir.
Artık öğretmenlik yoluna hazırlanabilirsiniz."""
}

# 📤 إرسال 3 رسائل للطالبة
async def send_feedback(context, student_id, level):
    # 1️⃣ التقييم
    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Seviyeniz

{levels[level]}

{messages[level]}"""
    )

    # 2️⃣ سجل
    await context.bot.send_message(
        chat_id=student_id,
        text="""📌 Takip Kaydı

Sizin için gelişim kaydı oluşturuldu.
Adım adım ilerlemeniz takip edilecektir."""
    )

    # 3️⃣ القناة
    await context.bot.send_message(
        chat_id=student_id,
        text="""📚 Dersler ve duyurular:

https://t.me/itkanakademi"""
    )

# ⭐ التقييم
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, level, message_id = query.data.split("_")
    message_id = int(message_id)

    student_id = student_messages.get(message_id)
    if not student_id:
        return

    await send_feedback(context, student_id, level)

    # حذف الأزرار + عرض النتيجة للمعلمة
    await query.edit_message_text(
        text=f"""✅ Değerlendirme gönderildi

📊 Seviye: {levels[level]}"""
    )

# ⚠️ إعادة الآية
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

    await query.message.reply_text("✅ Gönderildi")

# 📝 طلب الاسم والعمر
async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])
    student_id = student_messages.get(message_id)

    if not student_id:
        return

    await context.bot.send_message(
        chat_id=student_id,
        text="""📌 Lütfen tekrar yazınız:

👤 İsminiz
🪻 Yaşınız"""
    )

    await query.message.reply_text("✅ İstek gönderildi")

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
app.add_handler(MessageHandler(filters.VOICE, handle_voice))

app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))
app.add_handler(CallbackQueryHandler(handle_info, pattern="^info_"))

app.run_polling()
