import asyncio
import logging
import json
import os
import ccxt
import telegram
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from signals import check_signals

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Preliminary checks
required_env_vars = [
    'KUCOIN_API_KEY',
    'KUCOIN_API_SECRET',
    'KUCOIN_API_PASSPHRASE',
    'TELEGRAM_BOT_TOKEN',
    'CHAT_ID'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

logger.info("All required environment variables are set.")

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        logger.info("Configuration loaded successfully.")
except FileNotFoundError as e:
    logger.error(f"Configuration file not found: {e}")
    raise
except json.JSONDecodeError as e:
    logger.error(f"Error decoding JSON: {e}")
    raise

# Setup file logging handler
file_handler = logging.FileHandler('signals_log.txt')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Verify environment variables are loaded
kucoin_api_key = os.getenv('KUCOIN_API_KEY')
kucoin_api_secret = os.getenv('KUCOIN_API_SECRET')
kucoin_api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

logger.debug(f"KuCoin API Key: {kucoin_api_key}")
logger.debug(f"Telegram Bot Token: {telegram_bot_token}")
logger.debug(f"Chat ID: {chat_id}")

exchange = bot = None


def initialize_services():
    global exchange, bot
    try:
        logger.info("Initializing KuCoin client...")
        exchange = ccxt.kucoin({
            'apiKey': kucoin_api_key,
            'secret': kucoin_api_secret,
            'password': kucoin_api_passphrase
        })
        logger.info("KuCoin client initialized successfully.")
        logger.info("Initializing Telegram bot...")
        bot = telegram.Bot(token=telegram_bot_token)
        logger.info("Telegram bot initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise


async def periodic_signal_check():
    logger.info("Starting periodic signal check")
    try:
        await check_signals(config, exchange)
        logger.info("Signal checking completed.")
    except Exception as e:
        logger.error(f"Error during signal checking: {e}")


def main():
    logger.info("Initializing services...")
    initialize_services()
    scheduler = AsyncIOScheduler()
    logger.info("Scheduler initialized.")
    try:
        interval = config.get('signal_check_interval', 100)  # Default should be 100s now
        logger.debug(f"Fetched interval from config: {interval}")
        # Ensure interval is an integer and a positive value
        interval = int(interval)
        if interval <= 0:
            raise ValueError("Interval must be a positive integer")
        scheduler.add_job(periodic_signal_check, 'interval', seconds=interval)
        logger.info(f"Scheduled job to run every {interval} seconds.")
    except KeyError:
        logger.error("signal_check_interval is missing in the configuration")
        raise
    except ValueError as e:
        logger.error(f"Invalid interval value: {e}")
        raise
    scheduler.start()
    logger.info("Scheduler started.")
    logger.info("Crypto signals bot is running...")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown initiated...")
        scheduler.shutdown(wait=False)
        logger.info("Crypto signals bot stopped.")


# Example to run the function
if __name__ == "__main__":
    main()
