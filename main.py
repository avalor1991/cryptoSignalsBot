from dotenv import load_dotenv
import os
import numpy as np
import pandas as pd
import time
import ccxt
import asyncio
from telegram import Bot

# Load environment variables from .env file
load_dotenv()

# Load keys and tokens from environment variables
kucoin_api_key = os.getenv('KUCOIN_API_KEY')
kucoin_api_secret = os.getenv('KUCOIN_API_SECRET')
kucoin_api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

# Initialize clients
exchange = ccxt.kucoin({
    'apiKey': kucoin_api_key,
    'secret': kucoin_api_secret,
    'password': kucoin_api_passphrase
})
bot = Bot(token=telegram_bot_token)


# Fetch market data using ccxt
def fetch_market_data(trading_pair):
    try:
        since = exchange.parse8601(exchange.iso8601(time.time() - 24 * 60 * 60 * 1000))
        ohlcv = exchange.fetch_ohlcv(trading_pair, timeframe='15m', since=since)
        data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        return data
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None


def moving_average_crossover(data):
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    data['SMA_200'] = data['close'].rolling(window=200).mean()
    data['positions'] = np.where(data['SMA_50'] > data['SMA_200'], 1, -1)
    return data


def calculate_rsi(data, window=14):
    delta = data['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def bollinger_bands(data, window=20, num_std_dev=2):
    data['rolling_mean'] = data['close'].rolling(window=window).mean()
    data['rolling_std'] = data['close'].rolling(window=window).std()
    data['bollinger_upper'] = data['rolling_mean'] + (data['rolling_std'] * num_std_dev)
    data['bollinger_lower'] = data['rolling_mean'] - (data['rolling_std'] * num_std_dev)
    return data


async def send_signal(message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Error sending message: {e}")


async def check_signals(trading_pairs):
    for pair in trading_pairs:
        data = fetch_market_data(pair)
        if data is not None:
            mac = moving_average_crossover(data)
            rsi = calculate_rsi(data)
            bb_data = bollinger_bands(data)

            latest_signal = f"Trading Pair: {pair}\n"
            if mac['positions'].iloc[-1] == 1:
                latest_signal += f"Moving Average Crossover: Buy Signal\n"
            elif mac['positions'].iloc[-1] == -1:
                latest_signal += f"Moving Average Crossover: Sell Signal\n"
            if rsi.iloc[-1] < 30:
                latest_signal += f"RSI: Buy Signal (RSI={rsi.iloc[-1]:.2f})\n"
            elif rsi.iloc[-1] > 70:
                latest_signal += f"RSI: Sell Signal (RSI={rsi.iloc[-1]:.2f})\n"
            if data['close'].iloc[-1] < bb_data['bollinger_lower'].iloc[-1]:
                latest_signal += "Bollinger Bands: Buy Signal\n"
            elif data['close'].iloc[-1] > bb_data['bollinger_upper'].iloc[-1]:
                latest_signal += "Bollinger Bands: Sell Signal\n"
            if "Buy Signal" in latest_signal or "Sell Signal" in latest_signal:
                await send_signal(latest_signal)


async def main():
    trading_pairs = ["BTC/USDT", "ETH/USDT"]
    await check_signals(trading_pairs)


if __name__ == "__main__":
    asyncio.run(main())
