import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from groq import Groq

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")  # 👈 Your Telegram ID stored in .env

# Debug: check environment
print("BOT_TOKEN:", "Loaded" if BOT_TOKEN else "Missing")
print("GROQ_API_KEY:", "Loaded" if GROQ_API_KEY else "Missing")
print("ADMIN_ID:", ADMIN_ID if ADMIN_ID else "Missing")

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
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\nI'm your AI Community Bot 🤖\nSend me any message and I'll reply!"
    )
    print(f"User started bot -> ID: {user.id}, Name: {user.full_name}")

# Handle normal user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

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
# Admin Commands
# -------------------------------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message to all users (only admin can run this)."""
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /broadcast <your message>")
        return

    message = " ".join(context.args)
    # For now just echo to admin (later you can store user IDs in DB)
    await update.message.reply_text(f"✅ Broadcast sent: {message}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics (admin only)."""
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    await update.message.reply_text("📊 Bot is running fine! (Add more stats later)")

# -------------------------------
# Main function
# -------------------------------
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found. Check your .env file.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Normal commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Admin commands
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))

    print("Bot is running...")
    app.run_polling()