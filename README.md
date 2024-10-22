# Crypto Signals Bot

## Overview

The Crypto Signals Bot continuously monitors cryptocurrency markets and generates buy/sell signals based on various technical indicators. These signals are then sent to a Telegram bot to notify users.

## Project Structure

* `main.py` - The entry point of the application. It initializes the services (KuCoin API and Telegram Bot), sets up the scheduler for periodic signal checks, and starts the bot.

* `fetch_data.py` - Contains functions to fetch market data from the KuCoin API, including retries and error handling.

* `signals.py` - Implements the logic to analyze fetched market data using various technical indicators and generate trading signals.

* `notifications.py` - Handles sending messages to the Telegram bot.

* `indicators.py` - Contains functions to calculate technical indicators like moving average crossover, RSI, Bollinger Bands, and volume spikes.

* `requirements.txt` - Lists the Python dependencies required to run the bot.

* `config.json` - A configuration file that specifies settings like trading pairs, time intervals, and thresholds for signal generation.

* `.env` - Environment file storing sensitive data such as API keys and tokens.

* `signals_log.txt` - Log file for recording activities and errors.

* `README.md` - Documentation file (this file).

## Setup Instructions

### Step 1: Clone the Repository
### Step 2: Set Up Virtual Environment (Optional but recommended)
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
```

### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the root directory and add your API keys and tokens:
```dotenv
KUCOIN_API_KEY=your_kucoin_api_key
KUCOIN_API_SECRET=your_kucoin_api_secret
KUCOIN_API_PASSPHRASE=your_kucoin_api_passphrase
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_id
```

### Step 5: Configure Bot Settings
Edit `config.json` to configure trading pairs, thresholds, and intervals:
```json
{
  "trading_pairs": ["BTC/USDT", "ETH/USDT"],
  "signal_check_interval": 900,
  "short_ma_window": 9,
  "long_ma_window": 21,
  "rsi_window": 14,
  "bollinger_window": 20,
  "bollinger_std_dev": 2,
  "volume_spike_threshold": 1.5,
  "stop_loss_pct": 5
}
```

### Step 6: Run the Bot
```sh
python main.py
```

## File Descriptions

### `main.py`
Initializes and runs the bot. It sets up services, initializes the scheduler for periodic signal checks, and handles clean-up on exit.
- **initialize_services**: Sets up the KuCoin API client and the Telegram Bot client.
- **periodic_signal_check**: Periodically triggers the signal checking procedure.
- **main**: Starts the services and scheduler.

### `fetch_data.py`
Fetches market data for specific trading pairs from the KuCoin API.
- **fetch_market_data**: Fetches OHLCV (open-high-low-close-volume) data, handling retries and errors.

### `signals.py`
Analyzes market data and generates trading signals.
- **check_signals**: Fetches market data for multiple trading pairs and analyzes them with different technical indicators.
- **generate_signal**: Generates buy/sell signals based on the results of technical indicator calculations.

### `notifications.py`
Sends messages to the Telegram Bot.
- **send_signal**: Attempts to send a message to the Telegram Bot, with retries if necessary.

### `indicators.py`
Calculates various technical indicators.
- **moving_average_crossover**: Calculates short-term and long-term moving averages to identify crossover points.
- **calculate_rsi**: Calculates the Relative Strength Index (RSI).
- **bollinger_bands**: Calculates Bollinger Bands.
- **check_volume_spike**: Identifies sudden spikes in trading volume.

### `requirements.txt`
Lists necessary Python libraries for the bot.
- `ccxt`: For interacting with cryptocurrency exchanges.
- `telegram`: For sending messages via Telegram.
- `pandas`: For data manipulation.
- `apscheduler`: For scheduling periodic tasks.
- Additional libraries like `python-dotenv`, `requests`, `numpy`, etc.

### `config.json`
Contains configuration parameters for the bot's operation.
- **trading_pairs**: List of trading pairs to monitor.
- **signal_check_interval**: Interval in seconds for checking trading signals.
- **short_ma_window** and **long_ma_window**: Window sizes for moving average crossover.
- **rsi_window**: Window size for RSI calculation.
- **bollinger_window** and **bollinger_std_dev**: Settings for Bollinger Bands.
- **volume_spike_threshold**: Threshold for detecting volume spikes.
- **stop_loss_pct**: Percentage for calculating stop loss.

### `.env`
Stores sensitive data such as API keys and tokens.

### `signals_log.txt`
Log file for recording activities and errors.

## Running Tests
To ensure your Telegram bot integration works, you can use a simple test script:

#### `test_telegram_bot.py`
```python
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
```

Run the test script:
```sh
python test_telegram_bot.py
```

### Conclusion
If you followed all the steps correctly, your Crypto Signals Bot should be up and running, sending alerts to your Telegram bot with trading signals. If there are any issues or errors, refer to the logs in `signals_log.txt` for more details.