"""
==============================================
  TECHNICAL INDICATORS ENGINE
==============================================
7 powerful indicators with confluence scoring.
"""

import pandas as pd
import numpy as np
from config import *


def calculate_rsi(df, period=RSI_PERIOD):
    """RSI (Relative Strength Index) calculate karo"""
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(df, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL):
    """MACD + Signal Line + Histogram"""
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_emas(df):
    """Multiple EMAs calculate karo"""
    ema_fast = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    ema_medium = df['close'].ewm(span=EMA_MEDIUM, adjust=False).mean()
    ema_slow = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
    return ema_fast, ema_medium, ema_slow


def calculate_bollinger_bands(df, period=BB_PERIOD, std_dev=BB_STD):
    """Bollinger Bands calculate karo"""
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower


def calculate_stochastic_rsi(df, period=STOCH_RSI_PERIOD, k=STOCH_K, d=STOCH_D):
    """Stochastic RSI calculate karo"""
    rsi = calculate_rsi(df, period)
    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stoch_k = stoch_rsi.rolling(k).mean() * 100
    stoch_d = stoch_k.rolling(d).mean()
    return stoch_k, stoch_d


def calculate_atr(df, period=ATR_PERIOD):
    """ATR (Average True Range) - volatility measure"""
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def calculate_volume_analysis(df, period=VOLUME_MA_PERIOD):
    """Volume analysis - volume spike detection"""
    vol_ma = df['volume'].rolling(window=period).mean()
    vol_ratio = df['volume'] / vol_ma
    return vol_ma, vol_ratio


def calculate_vwap(df):
    """VWAP (Volume Weighted Average Price) - intraday"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    cumulative_tp_vol = (typical_price * df['volume']).cumsum()
    cumulative_vol = df['volume'].cumsum()
    vwap = cumulative_tp_vol / cumulative_vol
    return vwap


def analyze_signals(df):
    """
    Sare indicators run karo aur signal generate karo.
    Returns: dict with signal info
    """
    if len(df) < 60:
        return None

    # Calculate all indicators
    rsi = calculate_rsi(df)
    macd_line, signal_line, histogram = calculate_macd(df)
    ema_fast, ema_medium, ema_slow = calculate_emas(df)
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(df)
    stoch_k, stoch_d = calculate_stochastic_rsi(df)
    atr = calculate_atr(df)
    vol_ma, vol_ratio = calculate_volume_analysis(df)
    vwap = calculate_vwap(df)

    # Current values (last candle)
    current_close = df['close'].iloc[-1]
    current_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2]
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]
    current_histogram = histogram.iloc[-1]
    prev_histogram = histogram.iloc[-2]
    current_ema_fast = ema_fast.iloc[-1]
    current_ema_medium = ema_medium.iloc[-1]
    current_ema_slow = ema_slow.iloc[-1]
    current_bb_upper = bb_upper.iloc[-1]
    current_bb_lower = bb_lower.iloc[-1]
    current_bb_mid = bb_mid.iloc[-1]
    current_stoch_k = stoch_k.iloc[-1]
    current_stoch_d = stoch_d.iloc[-1]
    prev_stoch_k = stoch_k.iloc[-2]
    prev_stoch_d = stoch_d.iloc[-2]
    current_atr = atr.iloc[-1]
    current_vol_ratio = vol_ratio.iloc[-1]
    current_vwap = vwap.iloc[-1]

    # Check for NaN
    values = [current_rsi, current_macd, current_ema_fast, current_ema_slow,
              current_bb_upper, current_stoch_k, current_atr, current_vol_ratio]
    if any(pd.isna(v) for v in values):
        return None

    # ═══════════════════════════════════════════
    #  SIGNAL SCORING SYSTEM (7 Indicators)
    # ═══════════════════════════════════════════
    long_score = 0
    short_score = 0
    signals_detail = {}

    # 1️⃣ RSI Signal
    if current_rsi < RSI_OVERSOLD:
        long_score += 1
        signals_detail['RSI'] = f"🟢 OVERSOLD ({current_rsi:.1f})"
    elif current_rsi > RSI_OVERBOUGHT:
        short_score += 1
        signals_detail['RSI'] = f"🔴 OVERBOUGHT ({current_rsi:.1f})"
    elif current_rsi < 45:
        long_score += 0.5
        signals_detail['RSI'] = f"🟡 Bullish Zone ({current_rsi:.1f})"
    elif current_rsi > 55:
        short_score += 0.5
        signals_detail['RSI'] = f"🟡 Bearish Zone ({current_rsi:.1f})"
    else:
        signals_detail['RSI'] = f"⚪ Neutral ({current_rsi:.1f})"

    # 2️⃣ MACD Signal (Crossover)
    macd_cross_up = prev_macd < prev_signal and current_macd > current_signal
    macd_cross_down = prev_macd > prev_signal and current_macd < current_signal
    if macd_cross_up or (current_macd > current_signal and current_histogram > prev_histogram):
        long_score += 1
        signals_detail['MACD'] = f"🟢 Bullish {'Crossover!' if macd_cross_up else 'Momentum'}"
    elif macd_cross_down or (current_macd < current_signal and current_histogram < prev_histogram):
        short_score += 1
        signals_detail['MACD'] = f"🔴 Bearish {'Crossover!' if macd_cross_down else 'Momentum'}"
    else:
        signals_detail['MACD'] = "⚪ Neutral"

    # 3️⃣ EMA Trend (Fast > Medium > Slow = Bullish)
    if current_ema_fast > current_ema_medium > current_ema_slow:
        long_score += 1
        signals_detail['EMA'] = "🟢 Strong Uptrend (9>21>50)"
    elif current_ema_fast < current_ema_medium < current_ema_slow:
        short_score += 1
        signals_detail['EMA'] = "🔴 Strong Downtrend (9<21<50)"
    elif current_close > current_ema_medium:
        long_score += 0.5
        signals_detail['EMA'] = "🟡 Mild Bullish"
    elif current_close < current_ema_medium:
        short_score += 0.5
        signals_detail['EMA'] = "🟡 Mild Bearish"
    else:
        signals_detail['EMA'] = "⚪ Neutral"

    # 4️⃣ Bollinger Bands
    bb_width = (current_bb_upper - current_bb_lower) / current_bb_mid * 100
    if current_close <= current_bb_lower:
        long_score += 1
        signals_detail['BB'] = f"🟢 At Lower Band (squeeze: {bb_width:.1f}%)"
    elif current_close >= current_bb_upper:
        short_score += 1
        signals_detail['BB'] = f"🔴 At Upper Band (squeeze: {bb_width:.1f}%)"
    elif current_close < current_bb_mid:
        long_score += 0.3
        signals_detail['BB'] = f"🟡 Below Mid ({bb_width:.1f}%)"
    elif current_close > current_bb_mid:
        short_score += 0.3
        signals_detail['BB'] = f"🟡 Above Mid ({bb_width:.1f}%)"
    else:
        signals_detail['BB'] = "⚪ Neutral"

    # 5️⃣ Stochastic RSI
    stoch_cross_up = prev_stoch_k < prev_stoch_d and current_stoch_k > current_stoch_d
    stoch_cross_down = prev_stoch_k > prev_stoch_d and current_stoch_k < current_stoch_d
    if current_stoch_k < STOCH_OVERSOLD and stoch_cross_up:
        long_score += 1
        signals_detail['StochRSI'] = f"🟢 Oversold Crossover ({current_stoch_k:.0f})"
    elif current_stoch_k > STOCH_OVERBOUGHT and stoch_cross_down:
        short_score += 1
        signals_detail['StochRSI'] = f"🔴 Overbought Crossover ({current_stoch_k:.0f})"
    elif current_stoch_k < STOCH_OVERSOLD:
        long_score += 0.5
        signals_detail['StochRSI'] = f"🟡 Oversold ({current_stoch_k:.0f})"
    elif current_stoch_k > STOCH_OVERBOUGHT:
        short_score += 0.5
        signals_detail['StochRSI'] = f"🟡 Overbought ({current_stoch_k:.0f})"
    else:
        signals_detail['StochRSI'] = f"⚪ Neutral ({current_stoch_k:.0f})"

    # 6️⃣ Volume Spike
    if current_vol_ratio > VOLUME_SPIKE_THRESHOLD:
        # Volume spike - confirms the direction of other signals
        if long_score > short_score:
            long_score += 1
        elif short_score > long_score:
            short_score += 1
        signals_detail['Volume'] = f"🟢 Spike! ({current_vol_ratio:.1f}x avg)"
    else:
        signals_detail['Volume'] = f"⚪ Normal ({current_vol_ratio:.1f}x avg)"

    # 7️⃣ VWAP
    if current_close > current_vwap:
        long_score += 0.5
        signals_detail['VWAP'] = "🟢 Above VWAP (Bullish)"
    elif current_close < current_vwap:
        short_score += 0.5
        signals_detail['VWAP'] = "🔴 Below VWAP (Bearish)"
    else:
        signals_detail['VWAP'] = "⚪ At VWAP"

    # ═══════════════════════════════════════════
    #  FINAL SIGNAL DECISION
    # ═══════════════════════════════════════════
    max_score = max(long_score, short_score)
    total_possible = 7

    if max_score >= MIN_CONFIRMATIONS:
        if long_score > short_score:
            direction = "LONG 🟢📈"
            sl = current_close - (current_atr * ATR_SL_MULTIPLIER)
            tp1 = current_close + (current_atr * ATR_TP_MULTIPLIER)
            tp2 = current_close + (current_atr * ATR_TP_MULTIPLIER * 1.5)
            tp3 = current_close + (current_atr * ATR_TP_MULTIPLIER * 2.0)
        else:
            direction = "SHORT 🔴📉"
            sl = current_close + (current_atr * ATR_SL_MULTIPLIER)
            tp1 = current_close - (current_atr * ATR_TP_MULTIPLIER)
            tp2 = current_close - (current_atr * ATR_TP_MULTIPLIER * 1.5)
            tp3 = current_close - (current_atr * ATR_TP_MULTIPLIER * 2.0)

        # Confidence level
        confidence = (max_score / total_possible) * 100
        if confidence >= 85:
            strength = "🔥🔥🔥 ULTRA STRONG"
        elif confidence >= 70:
            strength = "🔥🔥 STRONG"
        elif confidence >= 55:
            strength = "🔥 MODERATE"
        else:
            strength = "⚡ WEAK"

        return {
            'direction': direction,
            'strength': strength,
            'confidence': f"{confidence:.0f}%",
            'long_score': long_score,
            'short_score': short_score,
            'entry': current_close,
            'stop_loss': sl,
            'take_profit_1': tp1,
            'take_profit_2': tp2,
            'take_profit_3': tp3,
            'atr': current_atr,
            'risk_reward': f"1:{ATR_TP_MULTIPLIER/ATR_SL_MULTIPLIER:.1f}",
            'details': signals_detail,
        }

    return None  # No strong signal
