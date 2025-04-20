from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# إعدادات
BOT_TOKEN = "7889664298:AAG8UGFv6X9Law5uWQxgBa4VwKxbcf6sSCU"  # التوكن
ADMIN_ID = 6350650382  # رقم حسابك على تيليجرام

# روابط محفوظة وردودها
custom_responses = {
    "https://www.tiktok.com/@user1/video/1234567890": "هذا فيديو رياكشن 1",
    "https://www.tiktok.com/@user2/video/9876543210": "وهذا فيديو ثاني معروف",
}

# مراحل جمع الاسم
ASK_NAME, ASK_SURNAME = range(2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا! شنو اسمك؟")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["first_name"] = update.message.text
    await update.message.reply_text("تمام، شنو اسم العائلة؟")
    return ASK_SURNAME

async def ask_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.message.text
    full_name = f"{context.user_data['first_name']} {context.user_data['last_name']}"
    username = update.effective_user.username or "No username"
    user_id = update.effective_user.id

    msg = f"شخص جديد بدأ المحادثة:\nالاسم: {full_name}\nيوزر: @{username}\nID: {user_id}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text(f"تم، حياك الله {full_name}!")
    return ConversationHandler.END

# الرد على كل الرسائل
async def chatgpt_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    username = update.effective_user.username or "No username"

    # تحقق من وجود رابط معروف
    for link, reply in custom_responses.items():
        if link in user_message:
            await update.message.reply_text("إي إي، أعرف ذا الفيديو!")
            await update.message.reply_text(reply)
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"@{username} أرسل رابط معروف:\n{link}")
            return

    # ترسل رسالته لك
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"@{username} قال:\n{user_message}")

# إلغاء
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_reply))

    app.run_polling()

if __name__ == "__main__":
    main()