import requests
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from environment variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "bQUBO5ZEUp4YkggwsvnGd0ThV5As6Jgj")  # Store securely
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7615026104:AAE90oYsqglCIBojs3Rqq81fcVk7keLEbVI")  # Store securely

# Function to get Mistral AI response
def get_mistral_response(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-tiny",  # Use "mistral-small" or "mistral-medium" for better responses
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)  # Set timeout
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't process that.")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Command handler for /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome! How can I assist you today?")

# AI response when mentioned in a group or in private chat
async def respond(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text

    # Check if the bot is mentioned or in a private chat
    if f"@{context.bot.username}" in user_message or update.message.chat.type == "private":
        clean_message = user_message.replace(f"@{context.bot.username}", "").strip()
        bot_response = get_mistral_response(clean_message)
        await update.message.reply_text(bot_response)

# Main function
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))

    # Register message handler (Only respond when mentioned or in private chat)
    application.add_handler(MessageHandler(filters.TEXT & (filters.Entity("mention") | filters.ChatType.PRIVATE), respond))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
