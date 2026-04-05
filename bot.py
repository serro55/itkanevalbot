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
NAME, AGE, VOICE = range(3)  # مراحل الاسم، العمر، الفويس

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
    return NAME

# الحصول على الاسم
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.isdigit():
        # أرسل رقم بدل الاسم
        context.user_data["age"] = text
        await update.message.reply_text("🪻 Lütfen isminizi yazınız:")
        return NAME
    context.user_data["name"] = text
    if "age" in context.user_data:
        await update.message.reply_text("🎧 Şimdi Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz.")
        return VOICE
    await update.message.reply_text("🪻 Lütfen yaşınızı yazınız:")
    return AGE

# الحصول على العمر
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("⚠️ Lütfen sadece rakam giriniz. Yaşınızı tekrar yazınız:")
        return AGE
    context.user_data["age"] = text
    await update.message.reply_text("🎧 Lütfen Fetih Suresi 29. ayetini ses kaydı olarak gönderiniz.")
    return VOICE

# استقبال الفويس والتحقق من الاسم والعمر
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice.file_id
    name = context.user_data.get("name")
    age = context.user_data.get("age")

    if not name or not age:
        missing = []
        if not name:
            missing.append("isim")
        if not age:
            missing.append("yaş")
        await update.message.reply_text(f"⚠️ Lütfen önce {' ve '.join(missing)} giriniz, sonra ses kaydınızı gönderin.")
        return

    # إرسال الصوت للمعلمة
    sent = await context.bot.send_voice(chat_id=GROUP_ID, voice=voice)
    student_messages[sent.message_id] = user.id
    username = user.username or "Bilinmiyor"

    keyboard = [
        [InlineKeyboardButton("⭐ Değerlendir", callback_data=f"rate_{sent.message_id}")],
        [InlineKeyboardButton("⚠️ Tekrar gönder", callback_data=f"return_{sent.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"👤 {name} (@{username})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # الرد التسلسلي للطالبة
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
        [InlineKeyboardButton("🔵📖 Kaide-i Nuraniyye", callback_data=f"level_nurani_{message_id}")],
        [InlineKeyboardButton("🟡 Başlangıç", callback_data=f"level_beginner_{message_id}")],
        [InlineKeyboardButton("🟠 Orta Seviye", callback_data=f"level_intermediate_{message_id}")],
        [InlineKeyboardButton("🔴 İleri Seviye", callback_data=f"level_advanced_{message_id}")]
    ]

    # إزالة الأزرار بعد الضغط
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text("📊 Seviye seçiniz:", reply_markup=InlineKeyboardMarkup(keyboard))

# 📊 تحديد المستوى وإرسال الرسائل الخاصة
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, level, message_id = query.data.split("_")
    message_id = int(message_id)
    student_id = student_messages.get(message_id)
    if not student_id:
        return
    name = context.user_data.get("name", "Bilinmiyor")
    age = context.user_data.get("age", "Bilinmiyor")

    levels = {
        "nurani": "🔵📖 Kaide-i Nuraniyye",
        "beginner": "🟡 Başlangıç",
        "intermediate": "🟠 Orta Seviye",
        "advanced": "🔴 İleri Seviye"
    }

    next_level_text = {
        "nurani": "🟡 Başlangıç seviyesine ulaşmanız",
        "beginner": "🟠 Orta seviyeye ulaşmanız",
        "intermediate": "🔴 İleri seviyeye ulaşmanız",
        "advanced": "👑 İtkan seviyesinde tam yetkinlik ve ardından öğretmenlik yolculuğuna başlamak"
    }

    if level == "nurani":
        level_message = f"""📊 Seviye Sonucunuz:
{levels[level]}

🌱 {name}, Kur’an yolculuğunuza sağlam bir temel atarak başlıyorsunuz.
Her adımınız sizi daha güçlü ve bilinçli bir okuyucu yapacak 💪
İyi bir başlangıç, ilerideki seviyelerin anahtarıdır 🔑
"""
    elif level == "advanced":
        level_message = f"""📊 Seviye Sonucunuz:
{levels[level]}

🌟 {name}, artık ileri seviyeye ulaştınız

Her öğrendiğiniz bilgi ve tilavetiniz bir emanettir 🕊️
İyi bir temelle ilerleyerek Kur’an’ı en güzel şekilde okuyabilirsiniz

🎯 Hedefiniz: Tam İtkan seviyesinde yetkinlik ve ardından öğretmenlik yolculuğuna başlamak 🧡
İtkan hazırlık kursuna katılarak öğrendiklerinizi aktarabilir ve başkalarına rehber olabilirsiniz 🌱
"""
    else:
        level_message = f"""📊 Seviye Sonucunuz:
{levels[level]}

🌸 Maşallah {name}, güzel bir ilerleme

🎯 Hedef:
{next_level_text[level]}
"""

    full_message = f"""{level_message}
📌 Sizin için bir gelişim dosyası oluşturuldu
📌 Tilavetinize dair tüm değerlendirme notları kaydedildi
🧕🏻 Seviyenize uygun öğretmenimize iletilecek ve sizin gelişiminiz adım adım takip edilecektir
🌱 Bu yolculukta yalnız değilsiniz
İtkan ailesi olarak her zaman yanınızdayız 🧡
📚 Seviyenize uygun dersleri ana kanalımızdan takip ederek bir üst seviyeye en kısa sürede ulaşabilirsiniz
📢 Kanalımız:
https://t.me/itkanakademi
🤲 Allah size Kur’an’ı en güzel şekilde okumayı nasip etsin
"""

    await context.bot.send_message(chat_id=student_id, text=full_message)

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

app.run_polling()
