import logging
import asyncio
import datetime
import pytz
from fetch_data import fetch_market_data
from indicators import moving_average_crossover, calculate_rsi, bollinger_bands, check_volume_spike
from notifications import send_signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_stop_loss(entry_price: float, pct: float) -> float:
    return entry_price * (1 - pct / 100)


def calculate_risk_to_reward(entry_price: float, stop_loss: float, target_price: float) -> float:
    risk = entry_price - stop_loss
    reward = target_price - entry_price
    return reward / risk if risk != 0 else None


def calculate_trade_size(total_balance: float, risk_percentage: float) -> float:
    return total_balance * risk_percentage / 100


def get_est_time():
    est = pytz.timezone('US/Eastern')
    current_est_time = datetime.datetime.now(est)
    return current_est_time.strftime('%I:%M %p (EST)')


async def check_signals(config: dict, exchange):
    logging.info("Checking trading pairs signals...")
    trading_pairs = config.get('trading_pairs', [])
    stop_loss_pct = config.get('stop_loss_pct')
    total_balance = config.get('total_balance', 10000)
    risk_percentage = config.get('risk_percentage', 2.0)
    if not trading_pairs or stop_loss_pct is None:
        logging.error("Configuration is missing required keys.")
        return
    try:
        signal_summary = []
        tasks = [fetch_market_data(pair, exchange) for pair in trading_pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for pair, data in zip(trading_pairs, results):
            if isinstance(data, Exception):
                logging.error(f"Error fetching data for {pair}: {data}")
                continue
            logging.info(f"Processing data for trading pair: {pair}")
            if data is not None and not data.empty:
                short_ma_window = config.get('short_ma_window', 50)
                long_ma_window = config.get('long_ma_window', 200)
                rsi_window = config.get('rsi_window', 14)
                bollinger_window = config.get('bollinger_window', 20)
                bollinger_std_dev = config.get('bollinger_std_dev', 2)
                volume_spike_threshold = config.get('volume_spike_threshold', 1.5)

                mac = moving_average_crossover(data, short_ma_window, long_ma_window)
                rsi = calculate_rsi(data, rsi_window)
                bb_data = bollinger_bands(data, bollinger_window, bollinger_std_dev)
                volume_spike = check_volume_spike(data, volume_spike_threshold)

                # Trend calculation
                trend_1h = determine_trend(data, config.get('1h_short_ma_window', 50),
                                           config.get('1h_long_ma_window', 200))

                trend_15m = determine_trend(data, config.get('15m_short_ma_window', 50),
                                            config.get('15m_long_ma_window', 200))

                signal = await generate_signal(pair, data, mac, rsi, bb_data, volume_spike, stop_loss_pct,
                                               total_balance, risk_percentage, trend_1h, trend_15m)
                if signal:
                    logging.info(f"Generated signal for {pair}: {signal}")
                    signal_summary.append(signal)
        if signal_summary:
            summary_message = "\n\n".join(signal_summary)
            logging.info(f"Sending signal summary: {summary_message}")
            try:
                await send_signal(summary_message)
            except Exception as e:
                logging.error(f"Error sending signal: {e}")
        else:
            logging.info("No signals generated.")
    except Exception as e:
        logging.error(f"Error in checking signals: {e}")


def determine_trend(data, short_window, long_window):
    """
    Determine the trend based on moving averages.
    """
    short_ma = data['close'].rolling(window=short_window).mean().iloc[-1]
    long_ma = data['close'].rolling(window=long_window).mean().iloc[-1]

    if short_ma > long_ma:
        return "Bullish"
    elif short_ma < long_ma:
        return "Bearish"
    else:
        return "Neutral"


async def generate_signal(pair: str, data: dict, mac: dict, rsi: float, bb_data: dict, volume_spike: bool,
                          stop_loss_pct: float, total_balance: float, risk_percentage: float,
                          trend_1h: str, trend_15m: str) -> str:
    signal_lines = [f"⚠️ **Trading Signal for {pair}** ⚠️"]
    trends = f"**Trend Overview**: {trend_1h} on 1-hour, {trend_15m} on 15-minute chart."
    signal_lines.append(trends)
    entry_price = data.get('close').iloc[-1]
    signal_generated = False
    risk_to_reward_ratio = None  # Ensure initialization

    def append_signal_section(indicator_name, signal_type, entry_price, stop_loss, target_price):
        nonlocal risk_to_reward_ratio
        risk_to_reward_ratio = calculate_risk_to_reward(entry_price, stop_loss, target_price)
        signal_lines.append(f"**{indicator_name}**:")
        signal_lines.append(f"{signal_type}")
        signal_lines.append(f"💰 Entry Price: ${entry_price:.5f}")
        signal_lines.append(f"🛑 Stop Loss: ${stop_loss:.5f}")

    if mac['positions'].iloc[-1] == 1:
        stop_loss_price = calculate_stop_loss(entry_price, stop_loss_pct)
        target_price = entry_price * 1.02  # Example target price: 2% above entry price
        append_signal_section("Moving Average Crossover", "🔵 Signal: Buy", entry_price, stop_loss_price, target_price)
        signal_generated = True
    elif mac['positions'].iloc[-1] == -1:
        stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
        target_price = entry_price * 0.98  # Example target price: 2% below entry price
        append_signal_section("Moving Average Crossover", "🔴 Signal: Sell", entry_price, stop_loss_price, target_price)
        signal_generated = True

    if rsi.iloc[-1] < 30:
        stop_loss_price = calculate_stop_loss(entry_price, stop_loss_pct)
        target_price = entry_price * 1.02  # Example target price
        signal_lines.append(f"**RSI**:")
        signal_lines.append(f"🔵 Signal: Buy (RSI={rsi.iloc[-1]:.2f})")
        signal_lines.append(f"🛑 Stop Loss: ${stop_loss_price:.5f}")
        signal_generated = True
    elif rsi.iloc[-1] > 70:
        stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
        target_price = entry_price * 0.98  # Example target price
        signal_lines.append(f"**RSI**:")
        signal_lines.append(f"🔴 Signal: Sell (RSI={rsi.iloc[-1]:.2f})")
        signal_lines.append(f"🛑 Stop Loss: ${stop_loss_price:.5f}")
        signal_generated = True

    if data['close'].iloc[-1] < bb_data['bollinger_lower'].iloc[-1]:
        stop_loss_price = calculate_stop_loss(entry_price, stop_loss_pct)
        target_price = entry_price * 1.02  # Example target price
        signal_lines.append("**Bollinger Bands**:")
        signal_lines.append(f"🔵 Signal: Buy")
        signal_lines.append(f"🛑 Stop Loss: ${stop_loss_price:.5f}")
        signal_generated = True
    elif data['close'].iloc[-1] > bb_data['bollinger_upper'].iloc[-1]:
        stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
        target_price = entry_price * 0.98  # Example target price
        signal_lines.append("**Bollinger Bands**:")
        signal_lines.append(f"🔴 Signal: Sell")
        signal_lines.append(f"🛑 Stop Loss: ${stop_loss_price:.5f}")
        signal_generated = True

    # Add Risk-to-Reward Ratio and Suggested Trade Size
    if risk_to_reward_ratio is not None:
        signal_lines.append(f"📊 **Risk-to-Reward Ratio**: {risk_to_reward_ratio:.5f}")

    # Fix missing trade size calculation
    suggested_trade_size = calculate_trade_size(total_balance, risk_percentage)
    signal_lines.append(f"💼 **Suggested Trade Size**: {suggested_trade_size:.5f} units")

    # Add current time in EST
    current_est_time = get_est_time()
    signal_lines.append(f"🕒 **Time of Signal**: {current_est_time}")

    # Add caution message for conflicting signals
    signal_lines.append("🚨 **Caution**: Conflicting signals from RSI and Bollinger Bands.")

    final_signal = "\n".join(signal_lines)
    return final_signal if signal_generated else None
