import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from groq import Groq

# -------------------------------
# Load environment variables
# -------------------------------
# Ensure .env path is correct
load_dotenv(dotenv_path="C:/Users/user/Desktop/AI_Community_Bot/.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Debug: make sure keys are loaded
print("BOT_TOKEN:", "Loaded" if BOT_TOKEN else "Missing")
print("GROQ_API_KEY:", "Loaded" if GROQ_API_KEY else "Missing")

# -------------------------------
# Initialize Groq client
# -------------------------------
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")
client = Groq(api_key=GROQ_API_KEY)

# -------------------------------
# Bot Handlers
# -------------------------------
# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm your AI Community Bot 🤖\nSend me any message and I'll reply!"
    )

# Handle normal messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Call Groq API to generate a reply
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": user_text}],
            max_tokens=200
        )
        reply = getattr(response.choices[0].message, "content", "Sorry, I couldn't generate a reply.")
    except Exception as e:
        reply = f"Error generating response: {e}"

    await update.message.reply_text(reply)

# -------------------------------
# Main function
# -------------------------------
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found. Check your .env file.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()