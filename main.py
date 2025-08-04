# main.py (Hedge Fund - Fully Trained)
import ccxt
import pandas as pd
import pandas_ta as ta
import time
import os

# --- Configuration ---
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')

# --- Exchange Setup ---
exchange = ccxt.binanceus({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True,
    },
})
exchange.load_markets()

# --- Trading & Strategy Parameters ---
TIMEFRAME = '4h'
ORDER_AMOUNT_USDT = 100
MIN_USDT_VOLUME = 500000

# --- Strategy Parameters (WINNING SETTINGS FROM HEDGE FUND OPTIMIZER) ---
SHORT_SMA_WINDOW = 50
LONG_SMA_WINDOW = 80
RSI_PERIOD = 14
RSI_OVERBOUGHT = 65
BBANDS_PERIOD = 20
BBANDS_STDDEV = 2
TRAILING_STOP_PERCENT = 0.03

def fetch_data(symbol, timeframe, limit):
    """Fetches historical OHLCV data."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if len(ohlcv) == 0: return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_indicators(df):
    """Calculates all technical indicators."""
    if df is None or len(df) < LONG_SMA_WINDOW: return None
    df['short_sma'] = df['close'].rolling(window=SHORT_SMA_WINDOW).mean()
    df['long_sma'] = df['close'].rolling(window=LONG_SMA_WINDOW).mean()
    df.ta.rsi(period=RSI_PERIOD, append=True)
    df.ta.bbands(length=BBANDS_PERIOD, std=BBANDS_STDDEV, append=True)
    return df

def find_top_performer():
    """Scans the market for the best coin to trade."""
    print("🔍 Scanning for top performing coins...")
    try:
        all_tickers = exchange.fetch_tickers()
        usdt_pairs = {
            symbol: ticker for symbol, ticker in all_tickers.items()
            if symbol.endswith('/USDT') and ticker.get('quoteVolume') and ticker['quoteVolume'] > MIN_USDT_VOLUME
        }
        if not usdt_pairs:
            print("No pairs found meeting the volume criteria.")
            return None
        top_performer = sorted(usdt_pairs.items(), key=lambda item: item[1]['change'], reverse=True)[0]
        print(f"🏆 Top performer found: {top_performer[0]} with a {top_performer[1]['change']:.2f}% change.")
        return top_performer[0]
    except Exception as e:
        print(f"An error occurred during market scan: {e}")
        return None

# --- Main Trading Logic ---
def main():
    """The main function for the trading bot."""
    print("Starting Hedge Fund Grade Bot (v4 - Fully Trained)...")
    
    in_position = False
    current_symbol = None
    buy_price = 0.0
    highest_price_since_buy = 0.0
    trailing_stop_price = 0.0
    
    while True:
        try:
            if not in_position:
                current_symbol = find_top_performer()
                if current_symbol is None:
                    print("Could not find a suitable coin. Retrying in 5 minutes.")
                    time.sleep(300)
                    continue
                print(f"✅ New target acquired: {current_symbol}. Starting analysis...")

            data = fetch_data(current_symbol, TIMEFRAME, LONG_SMA_WINDOW + 20)
            if data is None: time.sleep(60); continue

            data = calculate_indicators(data)
            if data is None: time.sleep(60); in_position = False; continue

            last_row = data.iloc[-1]
            previous_row = data.iloc[-2]
            
            print(f"\n--- [{pd.to_datetime('now', utc=True)}] Trading: {current_symbol} ---")
            print(f"Current Price: {last_row['close']:.4f}")
            print(f"Indicators: Short SMA: {last_row['short_sma']:.4f} | Long SMA: {last_row['long_sma']:.4f} | RSI: {last_row[f'RSI_{RSI_PERIOD}']:.2f} | Upper BBand: {last_row[f'BBU_{BBANDS_PERIOD}_{BBANDS_STDDEV:.1f}']:.4f}")
            print(f"In Position: {in_position}")
            if in_position: print(f"Position Info: Buy Price: {buy_price:.4f} | Highest Price: {highest_price_since_buy:.4f} | Trailing Stop: {trailing_stop_price:.4f}")

            # --- BUY SIGNAL ---
            if not in_position and last_row['short_sma'] > last_row['long_sma'] and previous_row['short_sma'] <= previous_row['long_sma']:
                if last_row[f'RSI_{RSI_PERIOD}'] < RSI_OVERBOUGHT:
                    if last_row['close'] > last_row[f'BBU_{BBANDS_PERIOD}_{BBANDS_STDDEV:.1f}']:
                        print(f"📈 All signals confirm! Placing BUY order for {current_symbol}.")
                        try:
                            buy_price = last_row['close']
                            highest_price_since_buy = buy_price
                            trailing_stop_price = highest_price_since_buy * (1 - TRAILING_STOP_PERCENT)
                            # UNCOMMENT THE LINE BELOW TO PLACE REAL ORDERS
                            # order = exchange.create_market_buy_order(current_symbol, ORDER_AMOUNT_USDT / buy_price)
                            print("--- SIMULATED BUY ORDER ---")
                            in_position = True
                        except Exception as e:
                            print(f"An error occurred placing buy order: {e}")
                    else:
                        print("SMA/RSI good, but waiting for Bollinger Band breakout.")
                else:
                    print(f"Golden Cross detected, but RSI is too high. Waiting.")

            # --- SELL LOGIC ---
            elif in_position:
                # Update the highest price and trailing stop
                if last_row['close'] > highest_price_since_buy:
                    highest_price_since_buy = last_row['close']
                    trailing_stop_price = highest_price_since_buy * (1 - TRAILING_STOP_PERCENT)
                    print(f"🚀 Price hit new high! Trailing Stop updated to ${trailing_stop_price:.4f}")

                # REASON 1: TRAILING STOP-LOSS TRIGGER
                if last_row['close'] <= trailing_stop_price:
                    print(f"🔥 Trailing Stop-Loss triggered! Placing SELL order for {current_symbol}.")
                    try:
                        # UNCOMMENT THE LINES BELOW TO PLACE REAL ORDERS
                        # base_currency = current_symbol.split('/')[0]
                        # balance = exchange.fetch_balance()
                        # amount_to_sell = balance[base_currency]['free']
                        # if amount_to_sell > 0:
                        #     exchange.create_market_sell_order(current_symbol, amount_to_sell)
                        print("--- SIMULATED SELL ORDER ---")
                        in_position = False
                        current_symbol = None
                    except Exception as e:
                        print(f"An error occurred during trailing stop sell: {e}")
                
                # REASON 2: DEATH CROSS TRIGGER (as a backup)
                elif last_row['short_sma'] < last_row['long_sma'] and previous_row['short_sma'] >= previous_row['long_sma']:
                    print(f"📉 Death Cross Detected! Placing SELL order for {current_symbol}.")
                    try:
                        # UNCOMMENT THE LINES BELOW TO PLACE REAL ORDERS
                        # base_currency = current_symbol.split('/')[0]
                        # balance = exchange.fetch_balance()
                        # amount_to_sell = balance[base_currency]['free']
                        # if amount_to_sell > 0:
                        #     exchange.create_market_sell_order(current_symbol, amount_to_sell)
                        print("--- SIMULATED SELL ORDER ---")
                        in_position = False
                        current_symbol = None
                    except Exception as e:
                        print(f"An error occurred during death cross sell: {e}")
            else:
                print("No trading signal. Holding or waiting.")

            print("---------------------------------------------------\n")
            time.sleep(300)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
