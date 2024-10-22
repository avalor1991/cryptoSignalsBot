import numpy as np
import pandas as pd


def moving_average_crossover(data, short_window=50, long_window=200):
    data['SMA_50'] = data['close'].rolling(window=short_window).mean()
    data['SMA_200'] = data['close'].rolling(window=long_window).mean()
    data['positions'] = np.where(data['SMA_50'].fillna(0) > data['SMA_200'].fillna(0), 1, -1)
    return data


def calculate_rsi(data, window=14):
    delta = data['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-10)  # Avoid division by zero
    rsi = 100 - (100 / (1 + rs))
    return rsi


def bollinger_bands(data, window=20, num_std_dev=2):
    data['rolling_mean'] = data['close'].rolling(window=window).mean()
    data['rolling_std'] = data['close'].rolling(window=window).std()
    data['bollinger_upper'] = data['rolling_mean'] + (data['rolling_std'] * num_std_dev)
    data['bollinger_lower'] = data['rolling_mean'] - (data['rolling_std'] * num_std_dev)
    return data


def check_volume_spike(data, threshold=1.5):
    if len(data) < 50:
        raise ValueError("Insufficient data points to calculate rolling average")
    avg_volume = data['volume'].rolling(window=50).mean()
    latest_volume = data['volume'].iloc[-1]
    return latest_volume > avg_volume.iloc[-1] * threshold
