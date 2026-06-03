import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Hugging Face API Setup
API_URL = "https://api-inference.huggingface.co/models/Vamsi/T5_Paraphrase_Paws"
HF_TOKEN = os.getenv("HF_TOKEN")
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am your Sentence Rewriter Bot. Send me any sentence, and I will rewrite it!"
    )

def rewrite_sentence(text: str) -> str:
    payload = {"inputs": f"paraphrase: {text} </s>"}
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # If the model is loading on Hugging Face's side, it tells us to wait
    result = response.json()
    if isinstance(result, dict) and "estimated_time" in result:
        return "The AI model is waking up on the server. Please try again in 20 seconds!"
        
    try:
        return result[0]['generated_text']
    except (KeyError, IndexError):
        return "Sorry, I couldn't rewrite that sentence. Try again."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_chat_action(action="typing")
    
    try:
        rewritten = rewrite_sentence(user_text)
        await update.message.reply_text(f"✨ **Rewritten:**\n{rewritten}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Something went wrong.")

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logging.error("No TELEGRAM_TOKEN found!")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Starting bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
