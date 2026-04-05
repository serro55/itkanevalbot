import os
import asyncio
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

NAME, AGE, VOICE = range(3)

# 🌸 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        """🔸️🔶️ İtkan | Kur’an Akademisi'ne hoş geldiniz

Kur’an tilavetiniz özenle değerlendirilecektir 📖🔍

🎯 Amacımız:
Sizi doğru seviyeden başlatıp en kısa sürede ilerletmek

💪 Unutmayın:
Düzenli çalışma ve istikrar başarıyı getirir

👤 Lütfen isminizi yazınız:"""
    )
    return NAME

# 👤 الاسم
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.isdigit():
        context.user_data["age"] = text
        await update.message.reply_text("🪻 Lütfen isminizi yazınız:")
        return NAME

    context.user_data["name"] = text

    if "age" in context.user_data:
        await update.message.reply_text("🎧 Şimdi Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz.")
        return VOICE

    await update.message.reply_text("🪻 Lütfen yaşınızı yazınız:")
    return AGE

# 🪻 العمر
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("⚠️ Lütfen sadece rakam giriniz.")
        return AGE

    context.user_data["age"] = text
    await update.message.reply_text("🎧 Lütfen Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz.")
    return VOICE

# 🎧 الفويس
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice.file_id

    name = context.user_data.get("name")
    age = context.user_data.get("age")

    if not name or not age:
        await update.message.reply_text("⚠️ Önce isminizi ve yaşınızı giriniz.")
        return

    username = user.username or "Bilinmiyor"

    sent = await context.bot.send_voice(chat_id=GROUP_ID, voice=voice)
    student_messages[sent.message_id] = user.id

    keyboard = [
        [InlineKeyboardButton("⭐ Değerlendir", callback_data=f"rate_{sent.message_id}")],
        [InlineKeyboardButton("⚠️ Tekrar gönder", callback_data=f"return_{sent.message_id}")],
        [InlineKeyboardButton("👤 İsim Hatırlat", callback_data=f"name_{sent.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"👤 {name} (@{username})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.send_message(
        chat_id=user.id,
        text="""🎧 Ses kaydınız başarıyla alındı

⏳ En kısa sürede değerlendirilecektir inşallah

🌱 Sabırlı olun, her kayıt sizi daha iyiye taşır 🧡"""
    )

    await asyncio.sleep(3)

    await context.bot.send_message(
        chat_id=user.id,
        text="""📢 Kanalımız:
https://t.me/itkanakademi"""
    )

# ⭐ التقييم
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

    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text(
        "📊 Seviye seçiniz:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📊 المستوى
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, level, message_id = query.data.split("_")
    message_id = int(message_id)

    student_id = student_messages.get(message_id)
    if not student_id:
        return

    name = "Bilinmiyor"  # نرسل الاسم للطالبة من user_data أو نترك افتراضي
    levels = {
        "nurani": "🔵📖 Kaide-i Nuraniyye",
        "beginner": "🟡 Başlangıç",
        "intermediate": "🟠 Orta Seviye",
        "advanced": "🔴 İleri Seviye"
    }

    await query.message.edit_reply_markup(reply_markup=None)

    # رسالة تأكيد للمعلمة
    await query.message.reply_text(
        f"✅ Değerlendirme gönderildi\n📊 Seçilen: {levels[level]}"
    )

    # رسالة للطالبة
    level_message = f"📊 Seviye Sonucunuz:\n{levels[level]}"
    await context.bot.send_message(chat_id=student_id, text=level_message)

# ⚠️ إعادة إرسال الآية
async def handle_return(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])
    student_id = student_messages.get(message_id)

    if not student_id:
        return

    await context.bot.send_message(
        chat_id=student_id,
        text="""⚠️ Lütfen tekrar gönderiniz

📖 Fetih Suresi 29. ayet

🎧 Ses kaydı olarak gönderiniz"""
    )

    await query.message.reply_text("🔁 Gönderildi")

# 👤 تذكير بالاسم (زر خاص بالمعلمة فقط)
async def handle_name_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])
    student_id = student_messages.get(message_id)

    if not student_id:
        return

    await context.bot.send_message(
        chat_id=student_id,
        text="""👤 Lütfen dikkat

İsminiz ve yaşınız eksikse lütfen:

1️⃣ İsminizi yazınız  
2️⃣ Yaşınızı yazınız  
3️⃣ Sonra tekrar ses kaydınızı gönderiniz 🎧"""
    )

    await query.message.reply_text("✅ İsim hatırlatma mesajı gönderildi")

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
            text=f"📊 Değerlendirme:\n\n{update.message.text}\n\n🌸 Devam edin 🧡"
        )

# 🚀 تشغيل
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        VOICE: [MessageHandler(filters.VOICE, handle_voice)]
    },
    fallbacks=[]
)

app.add_handler(conv)
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), group_reply))

app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))
app.add_handler(CallbackQueryHandler(handle_name_reminder, pattern="^name_"))

app.run_polling()
