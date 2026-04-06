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

CHANNEL_LINK = "https://t.me/itkanakademi"
SHARE_LINK = f"https://t.me/share/url?url={CHANNEL_LINK}&text=🌿 Bu kanalı tavsiye ederim, çok faydalı içerikler var inşaAllah"

# 🌿 البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌿 Hoş geldiniz, Allah muvaffak eylesin")
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
        "🎧 Lütfen Fetih Suresi 29. ayeti ses kaydı olarak gönderiniz.\n\nAllah izniyle birlikte dinleyip değerlendireceğiz."
    )

    return ConversationHandler.END

# 🎤 استقبال الصوت (voice + audio)
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if update.message.voice:
        file_id = update.message.voice.file_id
        is_voice = True
    elif update.message.audio:
        file_id = update.message.audio.file_id
        is_voice = False
    else:
        return

    name = context.user_data.get("name", "Bilinmiyor")
    age = context.user_data.get("age", "Bilinmiyor")

    # إرسال للمجموعة
    if is_voice:
        sent = await context.bot.send_voice(chat_id=GROUP_ID, voice=file_id)
    else:
        sent = await context.bot.send_audio(chat_id=GROUP_ID, audio=file_id)

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

    # رسالة للطالبة بعد الإرسال
    student_keyboard = [
        [InlineKeyboardButton("📣 Kanalı ziyaret et", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🤍 Ailenle ve arkadaşlarınla paylaş", url=SHARE_LINK)]
    ]

    await context.bot.send_message(
        chat_id=user.id,
        text="""✅ Ses kaydınız başarıyla gönderildi

🌷 MaşaAllah, emeğiniz çok kıymetli.
Allah izniyle değerlendirme en kısa sürede yapılacaktır.

🤍 Daha fazla kişinin faydalanması için,
inşaAllah kanal linkini aileniz ve arkadaşlarınızla paylaşabilirsiniz.
BarakAllah fikom.""",
        reply_markup=InlineKeyboardMarkup(student_keyboard)
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

# 🎯 المستويات
levels = {
    "nurani": "🔵📖 Kaide-i Nuraniyye",
    "beginner": "🟡 Başlangıç",
    "intermediate": "🟠 Orta Seviye",
    "advanced": "🔴 İleri Seviye"
}

# 💬 رسائل التشجيع
messages = {
    "nurani": """🌱 MaşaAllah, çok güzel bir başlangıç.
Allah izniyle sağlam bir temel atıyorsunuz.
Düzenli devam ederseniz inşaAllah çok güzel ilerlersiniz.""",

    "beginner": """🌷 MaşaAllah, güzel bir seviyedesiniz.
Düzenli tekrar ile inşaAllah daha da ilerleyeceksiniz.
Allah muvaffak eylesin.""",

    "intermediate": """📈 MaşaAllah, iyi bir seviyeye ulaşmışsınız.
Biraz daha gayret ile inşaAllah ileri seviyeye geçebilirsiniz.
BarakAllah fikom.""",

    "advanced": """🏆 MaşaAllah, çok güzel bir seviyedesiniz.

Öğrendiklerinizi koruyup uygulamanız çok kıymetli.
Allah izniyle artık öğretme yoluna da yaklaşmaktasınız.
Allah muvaffak eylesin."""
}

# 🎯 أهداف المستويات
goals = {
    "nurani": """🎯 Hedef (Başlangıç Seviyesi):
Harfleri doğru tanıma ve temel okuma alışkanlığı kazanma.
Allah izniyle düzenli tekrar ile bu seviyeye ulaşabilirsiniz.""",

    "beginner": """🎯 Hedef (Orta Seviye):
Tecvid kurallarına daha dikkat ederek akıcı okumaya geçmek.
İnşaAllah biraz daha pratik ile bunu başarabilirsiniz.""",

    "intermediate": """🎯 Hedef (İleri Seviye):
Daha düzgün, hatasız ve tecvidli bir okuma seviyesine ulaşmak.
Allah muvaffak eylesin, çok yakınsınız.""",

    "advanced": """🎯 Hedef:
Bilginizi pekiştirip başkalarına öğretmeye başlamak.
Allah izniyle bu ilmi yaymanız çok kıymetlidir."""
}

# 📤 إرسال التقييم
async def send_feedback(context, student_id, level):
    await context.bot.send_message(
        chat_id=student_id,
        text=f"""📊 Seviyeniz

{levels[level]}

{messages[level]}

{goals[level]}"""
    )

    await context.bot.send_message(
        chat_id=student_id,
        text="""📌 Takip Kaydı

MaşaAllah, sizin için bir gelişim kaydı oluşturuldu.
Allah izniyle ilerlemeniz düzenli olarak takip edilecektir."""
    )

    await context.bot.send_message(
        chat_id=student_id,
        text="""📚 Dersler ve duyurular için kanal:

https://t.me/itkanakademi

İnşaAllah takip ederek daha fazla fayda sağlayabilirsiniz."""
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
        text="""⚠️ Lütfen Fetih Suresi 29. ayeti tekrar gönderiniz.

Allah izniyle tekrar dinleyip değerlendireceğiz."""
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
🪻 Yaşınız

BarakAllah fikom."""
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

# يدعم voice + audio
app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

app.add_handler(CallbackQueryHandler(handle_rate, pattern="^rate_"))
app.add_handler(CallbackQueryHandler(handle_level, pattern="^level_"))
app.add_handler(CallbackQueryHandler(handle_return, pattern="^return_"))
app.add_handler(CallbackQueryHandler(handle_info, pattern="^info_"))

app.run_polling()
