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
    {"type": "riddle", "question": "What is one way of preparing prawns that you hate?", "answer": "tempura"},
    {"type": "location", "question": "Find and head to a shop that specialises in tempura for your next task / clue!"}, # tempura makino 01-223
    {"type": "task", "question": "EBI tempura refers to shrimp fried in tempura batter. This is the dish that wreaked havoc on the stomach of a younger Myat. \n\n Your challenge is: Spell E B I out with your body in front of the store. \n\n You will receive a reward after completion of this task."},
    {"type": "reward", "question": "You crushed it. And it wasn't embarrassing at all! \n\n🎁 Your reward: 1️⃣ A sweet treat of your choice from any shop in Jewel \nOR \n2️⃣ Declan has to spell out TEMPURA and you can record him."},
    {"type": "riddle", "question": "You love going into supermarkets and looking at the different aisles. What is the aisle that you are most drawn too?", "answer": "sweets"},
    {"type": "location", "question": "Let's go to that specific aisle in the supermarket."}, # NTUC b2-205
    {"type": "task", "question": "You're gonna love this task. Once you have read this message, you have 7 seconds to grab as many sweets as possible. GO!"},
    {"type": "reward", "question": "You're on a roll :). \n\n🎁 Your reward: You get all these sweets!"},
    {"type": "riddle", "question": "I am a hero without powers.\nIn a dark place I toiled for hours.\nTill the aching glow in my heart\n Shone out, my trademark.\nA billionaire alone in my tower.\n", "answer": "iron man"},
    {"type": "location", "question": "Now, head to the place where you and Declan took a photo in the Iron Man pose."},
    {"type": "task", "question": "Pose like Iron Man and have a new photo taken! \n\n You will receive a reward after completion of this task."},
    {"type": "reward", "question": "I love you 3000. (He loves her 3000) \n\n🎁 Your reward: You can ask Declan to do a *reasonable* embarrassing task."},
    {"type": "riddle", "question": "What character is this? 🎀", "answer": "hello kitty"},
    {"type": "location", "question": "We last saw Kitty somewhere in this building... Head there for your next task!"},
    {"type": "task", "question": "It was here where we last saw the sweet Hello Kitty. \n\nWith loss, it is important to be able to pick yourself up, smile, laugh, and move on. \n\nYour task is to make Declan laugh. You have 60 seconds.\n\n You will receive a reward after completion of this task."},
    {"type": "reward", "question": "Good work! It was probably quite easy tbh. \n\n🎁 Your reward: Dinner Time! Let Declan know what you'd like for dinner and we can all head there together!"},
    {"type": "location", "question": "Head to the dinner spot."},
    {"type": "riddle", "question": "Declan will ask you a riddle.", "answer": "nil"},
    {"type": "task", "question": "I heard that it was going to be someone's special day once the clock strikes midnight! Wow!\n\nI also heard that you will be 23 this year. Congratulations!\n\nNow for a tough challenge: Find an object around you that contains the number 23 — could be a sign, barcode, room number, or package. \n\n You will receive a reward after completion of this task."},
    {"type": "reward", "question": "You. Are. Amazing. You deserve everything good that is coming your way. \n\n🎁 Your reward: A bar of chocolate."}
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧩 Question:\n{challenge['question']}")
    elif challenge["type"] == "location" or challenge["type"] == "task":
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("✅ Complete")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📍 Task:\n{challenge['question']}", reply_markup=keyboard)
    elif challenge["type"] == "reward":
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("✅ Claimed")]],
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
    elif challenge["type"] == "task":
        if text == "✅ complete" or text == "complete":
            user_progress[user_id] += 1
            await update.message.reply_text("📍 Task marked complete.")
            await send_challenge(update, context, user_id)
        else:
            await update.message.reply_text("Please press '✅ Complete' after completing the task.")
    elif challenge["type"] == "reward":
        if text == "✅ claimed" or text == "claimed":
            user_progress[user_id] += 1
            await update.message.reply_text("🏆 Reward claimed.")
            await send_challenge(update, context, user_id)
        else:
            await update.message.reply_text("Please press '✅ Claimed' after receiving the reward.")

# Main function
def main():
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
