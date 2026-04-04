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

NAME, AGE = range(2)  # الآن نطلب الاسم والعمر
WAITING_FOR_NAME, WAITING_FOR_AGE, WAITING_FOR_VOICE = range(3)  # حالة الرسائل

# 🌸 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🔸️🔶️ İtkan | Kur’an Akademisi'ne hoş geldiniz

Kur’an tilavetiniz özenle değerlendirilecektir 📖🔍

🎯 Amacımız:
Sizi doğru seviyeden başlatıp en kısa sürede ilerletmek

💪 Unutmayın:
Düzenli çalışma ve istikrar başarıyı getirir

👤 Lütfen isminizi yazınız:"""
    )
    return WAITING_FOR_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🪻 Lütfen yaşınızı yazınız:")
    return WAITING_FOR_AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text(
        "🎧 Lütfen Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz."
    )
    return WAITING_FOR_VOICE

# 🎧 استقبال الصوت
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # التأكد من أن الطالبة أدخلت الاسم والعمر أولاً
    if "name" not in context.user_data or "age" not in context.user_data:
        await update.message.reply_text(
            "⚠️ Önce isminizi ve yaşınızı giriniz.\nLütfen /start ile başlayın."
        )
        return

    voice = update.message.voice.file_id
    name = context.user_data.get("name", "Bilinmiyor")
    age = context.user_data.get("age", "Bilinmiyor")
    username = user.username or "Bilinmiyor"

    # إرسال الفويس + معلومات الطالب للمعلمة فقط
    sent = await context.bot.send_voice(
        chat_id=GROUP_ID,
        voice=voice
    )
    student_messages[sent.message_id] = user.id

    keyboard = [
        [InlineKeyboardButton("⭐ Değerlendir", callback_data=f"rate_{sent.message_id}")],
        [InlineKeyboardButton("⚠️ Tekrar gönder", callback_data=f"return_{sent.message_id}")],
        [InlineKeyboardButton("📝 Yazılı Mesaj Gönder", callback_data=f"message_{sent.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"👤 {name} (@{username})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # 📩 رسالة للطالبة فقط
    await context.bot.send_message(
        chat_id=user.id,
        text="""🎧 Ses kaydınız başarıyla alındı

⏳ En kısa sürede değerlendirilecektir inşallah

🌱 Sabırlı olun, her kayıt sizi daha iyiye taşır 🧡"""
    )
    await asyncio.sleep(3)
    await context.bot.send_message(
        chat_id=user.id,
        text="""📢 Daha fazla kişiye ulaşmak ve hayra vesile olmak için kanalımızı paylaşabilirsiniz:
https://t.me/itkanakademi"""
    )

# ⭐ التقييم
async def handle_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])

    keyboard = [
        [InlineKeyboardButton("🔵📖 Kaide-i Nuraniyye (Başlangıç öncesi seviye)", callback_data=f"level_nurani_{message_id}")],
        [InlineKeyboardButton("🟡 Başlangıç", callback_data=f"level_beginner_{message_id}")],
        [InlineKeyboardButton("🟠 Orta Seviye", callback_data=f"level_intermediate_{message_id}")],
        [InlineKeyboardButton("🔴 İleri Seviye", callback_data=f"level_advanced_{message_id}")]
    ]

    # حذف لوحة الأزرار بعد الضغط
    await query.message.edit_reply_markup(reply_markup=None)

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

    name = context.user_data.get("name", "Bilinmiyor")
    levels = {
        "nurani": "🔵📖 Kaide-i Nuraniyye",
        "beginner": "🟡 Başlangıç",
        "intermediate": "🟠 Orta Seviye",
        "advanced": "🔴 İleri Seviye"
    }

    level_text = levels.get(level, "Bilinmiyor")

    # رسالة للمعلمة لتأكيد التقييم
    await query.message.reply_text(
        f"✅ {level_text} seviyesinde değerlendirme gönderildi."
    )

    # رسالة للطالبة
    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Seviye Sonucunuz: {level_text}

🌱 {name}, Kur’an yolculuğunuz adım adım takip edilecektir.
İtkan ailesi olarak her zaman yanınızdayız 🧡"""
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
        text="""⚠️ Lütfen dikkat

📖 İstenen ayet: Fetih Suresi 29. ayet

🎧 Lütfen tekrar gönderiniz

🤲 Allah yardımcınız olsun"""
    )

    await query.message.reply_text("🔁 Öğrenciye geri gönderildi.")

# 📝 إرسال نص للطالبة من المعلمة
async def handle_teacher_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_id = int(query.data.split("_")[1])
    student_id = student_messages.get(message_id)
    if not student_id:
        return

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Lütfen {student_id} numaralı öğrenciye gönderilecek mesajı yazın."
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

{update.message.text}

🌸 Gayretiniz çok kıymetli, devam edin 🧡

📢 Kanalımız:
https://t.me/itkanakademi"""
        )

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        WAITING_FOR_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        WAITING_FOR_VOICE: [MessageHandler(filters.VOICE, handle_voice)]
    },
    fallbacks=[]
)

app.add_handler(conv)
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), group_reply))

app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))
app.add_handler(CallbackQueryHandler(handle_teacher_message, pattern="^message_"))

app.run_polling()
