# backtest.py
import pandas as pd
import ccxt

# --- Configuration ---
SYMBOL_TO_TEST = 'ETH/USDT'  # Change this to the coin you want to test
TIMEFRAME = '1h'
EXCHANGE_NAME = 'binanceus' # <<< THIS IS THE ONLY CHANGE

# --- Strategy Parameters ---
SHORT_SMA_WINDOW = 20
LONG_SMA_WINDOW = 50

def fetch_historical_data(symbol, timeframe, limit=500):
    """Fetches a larger set of historical data for backtesting."""
    exchange = getattr(ccxt, EXCHANGE_NAME)()
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

def run_backtest(df):
    """Runs the SMA Crossover strategy on the historical data."""
    if df is None or len(df) < LONG_SMA_WINDOW:
        print("Not enough data to run backtest.")
        return

    # Calculate indicators
    df['short_sma'] = df['close'].rolling(window=SHORT_SMA_WINDOW).mean()
    df['long_sma'] = df['close'].rolling(window=LONG_SMA_WINDOW).mean()
    df.dropna(inplace=True) # Remove rows where SMAs couldn't be calculated

    # Simulation variables
    in_position = False
    equity = 1000.0  # Start with 1000 USDT
    coin_balance = 0.0
    trades = 0

    print(f"--- Starting Backtest for {SYMBOL_TO_TEST} ---")
    print(f"Initial Equity: ${equity:.2f} USDT")

    for i in range(1, len(df)):
        current_row = df.iloc[i]
        previous_row = df.iloc[i-1]

        # Buy Signal
        if not in_position and current_row['short_sma'] > current_row['long_sma'] and previous_row['short_sma'] <= previous_row['long_sma']:
            coin_balance = equity / current_row['close']
            equity = 0
            in_position = True
            trades += 1
            print(f"{current_row['timestamp']} - BUY at ${current_row['close']:.2f}")

        # Sell Signal
        elif in_position and current_row['short_sma'] < current_row['long_sma'] and previous_row['short_sma'] >= previous_row['long_sma']:
            equity = coin_balance * current_row['close']
            coin_balance = 0
            in_position = False
            print(f"{current_row['timestamp']} - SELL at ${current_row['close']:.2f} | New Equity: ${equity:.2f}")

    # If still in position at the end, calculate final equity
    if in_position:
        equity = coin_balance * df.iloc[-1]['close']

    print("--- Backtest Complete ---")
    print(f"Final Equity: ${equity:.2f} USDT")
    print(f"Total Trades: {trades}")
    print("-------------------------")


if __name__ == "__main__":
    historical_data = fetch_historical_data(SYMBOL_TO_TEST, TIMEFRAME)
    run_backtest(historical_data)