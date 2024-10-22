import os
import logging
from telegram import Bot
from telegram.error import TelegramError, NetworkError  # Importing additional NetworkError for connection issues
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

if telegram_bot_token is None or chat_id is None:
    logger.error("TELEGRAM_BOT_TOKEN and CHAT_ID environment variables must be set")
    raise EnvironmentError("TELEGRAM_BOT_TOKEN and CHAT_ID environment variables must be set")

bot = Bot(token=telegram_bot_token)
logger.debug(f"Telegram Bot initialized with token: {telegram_bot_token} and chat ID: {chat_id}")

async def send_signal(message, retries=3, retry_delay=5):
    logger.info(f"Attempting to send signal: {message}")
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Signal sent successfully on attempt {attempt + 1}: {message}")
            break
        except NetworkError as e:
            logger.error(f"NetworkError sending message on attempt {attempt + 1}: {e}")
            await asyncio.sleep(retry_delay)
        except TelegramError as e:
            logger.error(f"TelegramError sending message on attempt {attempt + 1}: {e}")
            await asyncio.sleep(retry_delay)        
        except Exception as e:
            logger.error(f"Unexpected error sending message on attempt {attempt + 1}: {e}")
            await asyncio.sleep(retry_delay)

# Example usage of the send_signal function within an async context
async def main():
    await send_signal("Test message")

if __name__ == "__main__":
    asyncio.run(main())
