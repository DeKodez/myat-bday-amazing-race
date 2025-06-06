from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Mixed challenge types
challenges = [
    {
        "type": "riddle",
        "question": "I’m tall when I’m young, and I’m short when I’m old. What am I?",
        "answer": "candle"
    },
    {
        "type": "location",
        "question": "Go to the fountain at Central Park. When you're there, press ✅ Complete.",
        "answer": "complete"
    },
    {
        "type": "riddle",
        "question": "What has to be broken before you can use it?",
        "answer": "egg"
    },
    {
        "type": "location",
        "question": "Find the red statue outside the museum. Press ✅ Complete when you're there.",
        "answer": "complete"
    }
]

# Store each user's challenge index
user_progress = {}

# Keyboard for location-based tasks
complete_keyboard = ReplyKeyboardMarkup([["✅ Complete"]], one_time_keyboard=True, resize_keyboard=True)

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    send_challenge(update, context, user_id)

def send_challenge(update: Update, context: CallbackContext, user_id: int):
    index = user_progress[user_id]
    if index >= len(challenges):
        update.message.reply_text("🎉 You’ve completed all tasks! Well done!", reply_markup=ReplyKeyboardRemove())
        return

    challenge = challenges[index]
    if challenge["type"] == "riddle":
        update.message.reply_text(f"🧠 Riddle #{index + 1}:\n{challenge['question']}", reply_markup=ReplyKeyboardRemove())
    elif challenge["type"] == "location":
        update.message.reply_text(f"📍 Task #{index + 1}:\n{challenge['question']}", reply_markup=complete_keyboard)

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if user_id not in user_progress:
        update.message.reply_text("Send /start to begin the Amazing Race.")
        return

    index = user_progress[user_id]
    challenge = challenges[index]

    if challenge["type"] == "riddle" and text == challenge["answer"]:
        user_progress[user_id] += 1
        update.message.reply_text("✅ Correct! On to the next one...")
        send_challenge(update, context, user_id)
    elif challenge["type"] == "location" and text in ["✅ complete", "complete"]:
        user_progress[user_id] += 1
        update.message.reply_text("📍 Task confirmed complete! Here's your next challenge:")
        send_challenge(update, context, user_id)
    else:
        update.message.reply_text("❌ Not quite! Try again or complete the task.")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send /start to begin. For location tasks, press '✅ Complete' once you're at the spot!")

def main():
    import os
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ Error: BOT_TOKEN environment variable not set.")
        return

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("Amazing Race Bot is running...")
    updater.idle()

if __name__ == '__main__':
    main()
