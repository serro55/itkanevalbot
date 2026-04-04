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

NAME, AGE = range(2)

# 🌸 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🔸️🔶️ İtkan | Kur’an Akademisi'ne hoş geldiniz

Kur’an tilavetiniz özenle değerlendirilecektir 📖🔍

👤 İsminizi & soyisminizi yazınız:"""
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🪻 Lütfen yaşınızı yazınız:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text(
        "🎧 Lütfen Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz."
    )
    return ConversationHandler.END

# ❌ منع الفويس بدون تسجيل
async def reject_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "name" not in context.user_data or "age" not in context.user_data:
        await update.message.reply_text(
            """⚠️ Lütfen önce kayıt olun

👤 İsminizi ve soyisminizi yazın
🪻 Ardından yaşınızı girin

Sonrasında ses kaydı gönderebilirsiniz 🎧"""
        )
        return True
    return False

# 🎧 استقبال الصوت
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_voice(update, context):
        return

    user = update.message.from_user
    voice = update.message.voice.file_id

    name = context.user_data.get("name")
    age = context.user_data.get("age")

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

    await context.bot.send_message(
        chat_id=user.id,
        text="""🎧 Ses kaydınız başarıyla alındı

⏳ En kısa sürede değerlendirilecektir inşallah"""
    )

# ⭐ التقييم
async def handle_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])

    keyboard = [
        [InlineKeyboardButton("🔵📖 Kaide-i Nuraniyye (Başlangıç öncesi)", callback_data=f"level_nurani_{message_id}")],
        [InlineKeyboardButton("🟡 Başlangıç", callback_data=f"level_beginner_{message_id}")],
        [InlineKeyboardButton("🟠 Orta Seviye", callback_data=f"level_intermediate_{message_id}")],
        [InlineKeyboardButton("🔴 İleri Seviye", callback_data=f"level_advanced_{message_id}")]
    ]

    await query.message.reply_text(
        "📊 Seviye seçiniz:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📊 اختيار المستوى
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

    # ✅ حذف الأزرار
    await query.message.edit_reply_markup(reply_markup=None)

    # ✅ رسالة للمعلمة
    await query.message.reply_text(
        f"✅ Seviye gönderildi: {levels[level]}"
    )

    # ✅ إرسال للطالبة
    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Seviye Sonucunuz:
{levels[level]}

🌱 Değerlendirmeniz tamamlandı
📚 Seviyenize uygun dersleri takip edebilirsiniz

📢 Kanal:
https://t.me/itkanakademi"""
    )

# ⚠️ إعادة الإرسال
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

📖 Fetih Suresi 29. ayet"""
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
            text=f"""📊 Değerlendirme:

{update.message.text}"""
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
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), group_reply))

app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))

app.run_polling()
