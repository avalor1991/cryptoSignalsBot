import os
from dotenv import load_dotenv
import logging
from telegram import Bot
import asyncio

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve environment variables
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

# Initialize Telegram bot
bot = Bot(token=telegram_bot_token)


async def test_telegram_bot():
    try:
        await bot.send_message(chat_id=chat_id, text="This is a test message from your Crypto Signals Bot!")
        logging.info("Test message sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send test message: {e}")


if __name__ == "__main__":
    asyncio.run(test_telegram_bot())
