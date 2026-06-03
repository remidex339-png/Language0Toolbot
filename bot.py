import os
import logging
import sys
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Force logs to print immediately to Render console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)

API_URL = "https://api-inference.huggingface.co/models/Vamsi/T5_Paraphrase_Paws"
HF_TOKEN = os.getenv("HF_TOKEN")
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Received /start command from user.")
    await update.message.reply_text(
        "Hi! I am your Sentence Rewriter Bot. Send me any sentence, and I will rewrite it!"
    )

def rewrite_sentence(text: str) -> str:
    if not HF_TOKEN:
        return "Error: Hugging Face API Token missing on the server configuration."
        
    payload = {"inputs": f"paraphrase: {text} </s>"}
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()
    
    if isinstance(result, dict) and "estimated_time" in result:
        return "The AI model is waking up on the server. Please try again in 20 seconds!"
        
    try:
        return result[0]['generated_text']
    except (KeyError, IndexError):
        return "Sorry, I couldn't rewrite that sentence. Try again."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logging.info(f"Received text to rewrite: {user_text}")
    await update.message.reply_chat_action(action="typing")
    
    try:
        rewritten = rewrite_sentence(user_text)
        await update.message.reply_text(f"✨ **Rewritten:**\n{rewritten}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await update.message.reply_text("Something went wrong.")

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        logging.critical("❌ CRITICAL ERROR: TELEGRAM_TOKEN environment variable is missing or empty!")
        sys.exit(1) # Force render logs to show a crash explicitly

    logging.info("Initializing Telegram Application...")
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("🚀 Bot is now polling for messages...")
    application.run_polling()

if __name__ == '__main__':
    main()
