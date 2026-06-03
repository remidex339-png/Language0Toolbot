import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load the AI paraphrasing model (this might take a moment on first boot)
print("Loading AI Model...")
MODEL_NAME = "Vamsi/T5_Paraphrase_Paws"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am your Sentence Rewriter Bot. Send me any sentence, and I will rewrite it while keeping the original meaning!"
    )

# Paraphrase function
def rewrite_sentence(text: str) -> str:
    text = "paraphrase: " + text + " </s>"
    inputs = tokenizer.encode(text, return_tensors="pt", max_length=256, truncation=True)
    outputs = model.generate(inputs, max_length=256, num_beams=4, num_return_sequences=1, early_stopping=True)
    sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sentence

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_chat_action(action="typing")
    
    try:
        rewritten = rewrite_sentence(user_text)
        await update.message.reply_text(f"✨ **Rewritten:**\n{rewritten}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Sorry, I encountered an error trying to rewrite that.")

def main():
    # Get token from environment variables (secure for Render)
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Render uses dynamic ports, but for a simple polling bot, we just run polling
    application.run_polling()

if __name__ == '__main__':
    main()
