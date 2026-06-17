"""
==============================================
  BINANCE FUTURES SIGNAL BOT - CONFIGURATION
==============================================
Apni Binance API keys yahan daalein.
Ye bot sirf READ-ONLY data use karta hai,
koi trade execute NAHI karega.
"""

# ─── Binance API Keys ───────────────────────────
# Binance se API key banayein (Futures enabled hona chahiye)
# https://www.binance.com/en/my/settings/api-management
BINANCE_API_KEY = "comg6ryeDgJCgfmF5cduCAuGFIYkJx1kKLu7kZLKsUistqL3tArCFXJ78zaAySBH"
BINANCE_API_SECRET = "dIRZFd4FffClPPPkX767hhpyvg8uk1Xh9sNd6WZTDsYoJKnBIePc6A4UeDEWwhIu"

# ─── Trading Settings ───────────────────────────
TIMEFRAME = "15m"               # Candle timeframe: 1m, 5m, 15m, 1h, 4h
CANDLE_LIMIT = 200              # Kitni candles fetch karni hain (indicators ke liye)
SCAN_INTERVAL = 60              # Kitne seconds baad rescan kare

# ─── Filter Settings ────────────────────────────
MIN_VOLUME_USDT = 5_000_000     # Minimum 24h volume (USDT) - low volume coins skip
TOP_N_COINS = 0               # Top N coins by volume scan karo (sab ke liye 0)
QUOTE_ASSET = "USDT"            # Quote currency filter

# ─── Signal Strength ────────────────────────────
# Signal tab aaye jab minimum itne indicators agree karein
MIN_CONFIRMATIONS = 6           # 6 out of 7 indicators must agree (adjustable)

# ─── Indicator Parameters ───────────────────────
# RSI
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# EMA
EMA_FAST = 9
EMA_MEDIUM = 21
EMA_SLOW = 50

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2.0

# Stochastic RSI
STOCH_RSI_PERIOD = 14
STOCH_K = 3
STOCH_D = 3
STOCH_OVERBOUGHT = 80
STOCH_OVERSOLD = 20

# ATR (Average True Range) - for Stop Loss / Take Profit
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5        # Stop Loss = ATR * multiplier
ATR_TP_MULTIPLIER = 2.5        # Take Profit = ATR * multiplier

# Volume
VOLUME_MA_PERIOD = 20           # Volume moving average period
VOLUME_SPIKE_THRESHOLD = 1.5   # Volume current bar / MA > threshold = spike

# ─── Gmail Settings (FREE) ──────────────────
# Step 1: Gmail mein 2-Step Verification ON karo
# Step 2: App Password banao (neeche guide hai)
GMAIL_ADDRESS = "moiza2245@gmail.com"                # Apna Gmail address dalo
GMAIL_APP_PASSWORD = "jgcr qepm evtm arbo"            # App Password dalo