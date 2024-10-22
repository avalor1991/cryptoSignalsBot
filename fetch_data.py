import asyncio
import time
import pandas as pd
import logging


async def fetch_market_data(trading_pair, exchange, retries=3, retry_delay=5):
    for attempt in range(retries):
        try:
            # Corrected time calculation
            since = int(time.time() - (24 * 60 * 60)) * 1000  # Convert to milliseconds
            since = exchange.parse8601(exchange.iso8601(since))
            ohlcv = exchange.fetch_ohlcv(trading_pair, timeframe='15m', since=since)

            # Ensure ohlcv has the correct structure (list of lists)
            if not ohlcv or not all(isinstance(row, list) and len(row) == 6 for row in ohlcv):
                raise ValueError("Invalid OHLCV data structure")

            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            return data

        except (ValueError, TypeError, AttributeError) as e:
            logging.error(f"Error fetching market data for {trading_pair}, attempt {attempt + 1}: {e}")
            await asyncio.sleep(retry_delay)

        except Exception as e:
            logging.error(f"Unexpected error fetching market data for {trading_pair}, attempt {attempt + 1}: {e}")
            await asyncio.sleep(retry_delay)

    return None  # Return None after all retries
