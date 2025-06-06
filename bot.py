import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ContextTypes,
    filters,
)
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Sample challenges (can be expanded)
challenges = [
    {"type": "riddle", "question": "I speak without a mouth and hear without ears. What am I?", "answer": "echo"},
    {"type": "location", "question": "Go to the nearest park and press 'Complete'."},
    {"type": "riddle", "question": "I have keys but no locks. I have space but no rooms. What am I?", "answer": "keyboard"},
    {"type": "location", "question": "Go to a library and press 'Complete'."}
]

user_progress = {}

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await send_challenge(update, context, user_id)

# Function: send next challenge
async def send_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    index = user_progress[user_id]
    if index >= len(challenges):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🎉 Congratulations! You’ve completed all challenges.")
        return

    challenge = challenges[index]

    if challenge["type"] == "riddle":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧩 Riddle:\n{challenge['question']}")
    elif challenge["type"] == "location":
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("✅ Complete")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📍 Task:\n{challenge['question']}", reply_markup=keyboard)

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your answers to riddles, or press ✅ Complete after visiting the required location.")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        await update.message.reply_text("Please start the race with /start.")
        return

    index = user_progress[user_id]
    if index >= len(challenges):
        return

    challenge = challenges[index]
    text = update.message.text.strip().lower()

    if challenge["type"] == "riddle":
        if text == challenge["answer"].lower():
            user_progress[user_id] += 1
            await update.message.reply_text("✅ Correct!")
            await send_challenge(update, context, user_id)
        else:
            await update.message.reply_text("❌ Try again!")
    elif challenge["type"] == "location":
        if text == "✅ complete" or text == "complete":
            user_progress[user_id] += 1
            await update.message.reply_text("📍 Task marked complete.")
            await send_challenge(update, context, user_id)
        else:
            await update.message.reply_text("Please press '✅ Complete' after reaching the location.")

# Main function
def main():
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
