#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🚀 BINANCE FUTURES SIGNAL INDICATOR BOT 🚀            ║
║   ─────────────────────────────────────────────────────  ║
║   📊 7 Indicators Confluence System                     ║
║   📈 RSI | MACD | EMA | BB | StochRSI | Volume | VWAP  ║
║   ⏱️  15m Timeframe | All USDT Futures Pairs            ║
║   🎯 Auto SL/TP with ATR-based calculation              ║
╚══════════════════════════════════════════════════════════╝
"""

import sys
import time
import os
from datetime import datetime

import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
from colorama import init, Fore, Back, Style

from config import *
from indicators import analyze_signals
from email_sender import send_email_signal

# Colorama initialize
init(autoreset=True)

# ─── Colors ──────────────────────────────────
GREEN = Fore.GREEN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
CYAN = Fore.CYAN + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
MAGENTA = Fore.MAGENTA + Style.BRIGHT
BLUE = Fore.BLUE + Style.BRIGHT
RESET = Style.RESET_ALL


def print_banner():
    """Fancy banner print karo"""
    banner = f"""
{CYAN}╔══════════════════════════════════════════════════════════════╗
║{YELLOW}  🚀 BINANCE FUTURES SIGNAL INDICATOR BOT{CYAN}                     ║
║{WHITE}  ─────────────────────────────────────────────────────────── {CYAN}║
║{GREEN}  📊 7 Indicators: RSI | MACD | EMA | BB | StochRSI | Vol   {CYAN}║
║{GREEN}  ⏱️  Timeframe: {TIMEFRAME} | Min Confirmations: {MIN_CONFIRMATIONS}/7{CYAN}             ║
║{MAGENTA}  🎯 Auto SL/TP | ATR-Based Risk Management{CYAN}                  ║
║{RED}  ⚠️  DISCLAIMER: Ye sirf signals hain, 100% guarantee nahi! {CYAN}║
╚══════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)


def connect_binance():
    """Binance se connect karo"""
    print(f"{CYAN}🔌 Binance se connect ho raha hai...{RESET}")
    try:
        client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        # Test connection
        client.ping()
        server_time = client.get_server_time()
        print(f"{GREEN}✅ Binance se connect ho gaya!{RESET}")
        return client
    except BinanceAPIException as e:
        print(f"{RED}❌ Binance API Error: {e.message}{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Connection Error: {e}{RESET}")
        sys.exit(1)


def get_futures_symbols(client):
    """Sare USDT futures pairs fetch karo"""
    print(f"{CYAN}📋 Futures pairs fetch ho rahay hain...{RESET}")
    try:
        exchange_info = client.futures_exchange_info()
        symbols = []
        for s in exchange_info['symbols']:
            if (s['quoteAsset'] == QUOTE_ASSET and
                s['status'] == 'TRADING' and
                s['contractType'] == 'PERPETUAL'):
                symbols.append(s['symbol'])

        # Volume ke basis pe sort karo agar TOP_N set hai
        if TOP_N_COINS > 0:
            tickers = client.futures_ticker()
            ticker_map = {t['symbol']: float(t['quoteVolume']) for t in tickers}
            symbols = [s for s in symbols if s in ticker_map]
            symbols.sort(key=lambda x: ticker_map.get(x, 0), reverse=True)

            # Min volume filter
            symbols = [s for s in symbols if ticker_map.get(s, 0) >= MIN_VOLUME_USDT]
            symbols = symbols[:TOP_N_COINS]

        print(f"{GREEN}✅ {len(symbols)} futures pairs mil gaye!{RESET}")
        return symbols
    except Exception as e:
        print(f"{RED}❌ Error fetching symbols: {e}{RESET}")
        return []


def get_klines(client, symbol, interval=TIMEFRAME, limit=CANDLE_LIMIT):
    """Candlestick data fetch karo"""
    try:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        return None


def format_price(price):
    """Price ko smart format karo"""
    if price >= 1000:
        return f"{price:,.2f}"
    elif price >= 1:
        return f"{price:.4f}"
    elif price >= 0.01:
        return f"{price:.6f}"
    else:
        return f"{price:.8f}"


def print_signal(symbol, signal):
    """Signal ko beautiful format mein print karo"""
    is_long = "LONG" in signal['direction']
    color = GREEN if is_long else RED
    bg = Back.GREEN if is_long else Back.RED

    separator = f"{color}{'═' * 62}{RESET}"

    print(f"\n{separator}")
    print(f"{bg}{WHITE}  🎯 SIGNAL FOUND: {symbol}  {RESET}")
    print(f"{separator}")

    print(f"  {WHITE}Direction  : {color}{signal['direction']}{RESET}")
    print(f"  {WHITE}Strength   : {YELLOW}{signal['strength']}{RESET}")
    print(f"  {WHITE}Confidence : {MAGENTA}{signal['confidence']} ({signal['long_score']:.1f}L / {signal['short_score']:.1f}S){RESET}")
    print(f"  {WHITE}Entry      : {CYAN}{format_price(signal['entry'])}{RESET}")
    print(f"  {WHITE}Stop Loss  : {RED}✋ {format_price(signal['stop_loss'])}{RESET}")
    print(f"  {WHITE}TP 1       : {GREEN}🎯 {format_price(signal['take_profit_1'])}{RESET}")
    print(f"  {WHITE}TP 2       : {GREEN}🎯 {format_price(signal['take_profit_2'])}{RESET}")
    print(f"  {WHITE}TP 3       : {GREEN}🎯 {format_price(signal['take_profit_3'])}{RESET}")
    print(f"  {WHITE}R:R Ratio  : {YELLOW}{signal['risk_reward']}{RESET}")
    print(f"  {WHITE}ATR        : {BLUE}{format_price(signal['atr'])}{RESET}")

    print(f"\n  {WHITE}📊 Indicator Details:{RESET}")
    for name, detail in signal['details'].items():
        print(f"    {WHITE}{name:10s}: {detail}{RESET}")

    print(f"{separator}\n")


def scan_all_symbols(client, symbols):
    """Sare symbols scan karo aur signals dhundo"""
    signals_found = []
    total = len(symbols)

    print(f"\n{CYAN}{'═' * 62}{RESET}")
    print(f"{YELLOW}  🔍 SCANNING {total} PAIRS | Timeframe: {TIMEFRAME} | Time: {datetime.now().strftime('%H:%M:%S')}{RESET}")
    print(f"{CYAN}{'═' * 62}{RESET}")

    for i, symbol in enumerate(symbols, 1):
        # Progress bar
        progress = int((i / total) * 40)
        bar = f"{'█' * progress}{'░' * (40 - progress)}"
        sys.stdout.write(f"\r  {CYAN}[{bar}] {i}/{total} - {symbol:15s}{RESET}")
        sys.stdout.flush()

        df = get_klines(client, symbol)
        if df is None or len(df) < 60:
            continue

        signal = analyze_signals(df)
        if signal:
            signals_found.append((symbol, signal))

        # Rate limiting - Binance API limit avoid karo
        time.sleep(0.1)

    # Clear progress bar
    sys.stdout.write(f"\r{' ' * 80}\r")
    sys.stdout.flush()

    return signals_found


def print_summary(signals_found, scan_number):
    """Summary print karo"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not signals_found:
        print(f"\n{YELLOW}  ⚠️  Scan #{scan_number} Complete @ {timestamp}{RESET}")
        print(f"{YELLOW}  📭 Koi strong signal nahi mila. {MIN_CONFIRMATIONS}/7 confirmations chahiye.{RESET}")
        print(f"{YELLOW}  ⏳ Next scan {SCAN_INTERVAL} seconds mein...{RESET}")
    else:
        # Sort by confidence (highest first)
        signals_found.sort(key=lambda x: max(x[1]['long_score'], x[1]['short_score']), reverse=True)

        print(f"\n{GREEN}{'═' * 62}{RESET}")
        print(f"{GREEN}  ✅ Scan #{scan_number} Complete @ {timestamp}{RESET}")
        print(f"{GREEN}  📬 {len(signals_found)} SIGNALS Found!{RESET}")
        print(f"{GREEN}{'═' * 62}{RESET}")

        for symbol, signal in signals_found:
            print_signal(symbol, signal)
            # Email pe bhi bhejo
            send_email_signal(symbol, signal)

        # Quick summary table
        print(f"\n{CYAN}  📊 QUICK SUMMARY:{RESET}")
        print(f"  {WHITE}{'Symbol':15s} {'Direction':15s} {'Confidence':12s} {'Entry':15s} {'Strength'}{RESET}")
        print(f"  {WHITE}{'─' * 70}{RESET}")
        for symbol, signal in signals_found:
            is_long = "LONG" in signal['direction']
            color = GREEN if is_long else RED
            dir_text = "🟢 LONG" if is_long else "🔴 SHORT"
            print(f"  {color}{symbol:15s} {dir_text:15s} {signal['confidence']:12s} {format_price(signal['entry']):15s} {signal['strength']}{RESET}")


def main():
    """Main bot loop"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()

    # Binance connect
    client = connect_binance()

    # Futures symbols fetch
    symbols = get_futures_symbols(client)
    if not symbols:
        print(f"{RED}❌ Koi futures pair nahi mila. Config check karo.{RESET}")
        sys.exit(1)

    scan_number = 0

    while True:
        try:
            scan_number += 1

            # Scan all symbols
            signals_found = scan_all_symbols(client, symbols)

            # Print results
            print_summary(signals_found, scan_number)

            # Wait for next scan
            print(f"\n{CYAN}  ⏳ Next scan {SCAN_INTERVAL} seconds mein... (Ctrl+C to stop){RESET}")
            print(f"{CYAN}{'─' * 62}{RESET}")
            time.sleep(SCAN_INTERVAL)

            # Refresh symbols every 10 scans
            if scan_number % 10 == 0:
                symbols = get_futures_symbols(client)

        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}  👋 Bot band ho raha hai. Khuda Hafiz!{RESET}")
            sys.exit(0)
        except BinanceAPIException as e:
            print(f"\n{RED}  ❌ Binance Error: {e.message}{RESET}")
            print(f"{YELLOW}  ⏳ 30 seconds baad retry...{RESET}")
            time.sleep(30)
        except Exception as e:
            print(f"\n{RED}  ❌ Error: {e}{RESET}")
            print(f"{YELLOW}  ⏳ 10 seconds baad retry...{RESET}")
            time.sleep(10)


if __name__ == "__main__":
    main()
