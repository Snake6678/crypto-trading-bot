# optimizer.py (v4 - Hedge Fund Edition)
import pandas as pd
import pandas_ta as ta
import ccxt
import itertools

# --- Configuration ---
SYMBOL_TO_TEST = 'ETH/USDT'
TIMEFRAME = '4h'
EXCHANGE_NAME = 'binanceus'
DATA_FETCH_LIMIT = 750

# --- Optimization Parameter Ranges ---
# Define the different values you want to test for each parameter.
SHORT_SMA_VALUES = [40, 50]
LONG_SMA_VALUES = [60, 80]
RSI_OVERBOUGHT_VALUES = [65, 70]
BBANDS_PERIOD_VALUES = [20] # Standard is 20, often not changed
BBANDS_STDDEV_VALUES = [2]  # Standard is 2, often not changed
TRAILING_STOP_VALUES = [0.03, 0.05] # Test 3% and 5% trailing stop

def fetch_historical_data(symbol, timeframe, limit):
    """Fetches historical data for backtesting."""
    exchange = getattr(ccxt, EXCHANGE_NAME)()
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

def run_single_backtest(df, params):
    """Runs one backtest with a specific set of parameters."""
    # Extract parameters from the dictionary
    short_sma = params['short_sma']
    long_sma = params['long_sma']
    rsi_overbought = params['rsi_overbought']
    bbands_period = params['bbands_period']
    bbands_stddev = params['bbands_stddev']
    trailing_stop_percent = params['trailing_stop']

    data = df.copy()
    
    # Calculate Indicators
    data['short_sma'] = data['close'].rolling(window=short_sma).mean()
    data['long_sma'] = data['close'].rolling(window=long_sma).mean()
    data.ta.rsi(period=14, append=True) # Standard RSI period is 14
    data.ta.bbands(length=bbands_period, std=bbands_stddev, append=True)
    data.dropna(inplace=True)

    if data.empty: return 0

    in_position = False
    equity = 1000.0
    buy_price = 0.0
    highest_price_since_buy = 0.0
    trailing_stop_price = 0.0

    for i in range(1, len(data)):
        current_row = data.iloc[i]
        previous_row = data.iloc[i-1]

        # Buy Signal
        if not in_position and current_row['short_sma'] > current_row['long_sma'] and previous_row['short_sma'] <= previous_row['long_sma']:
            if current_row['RSI_14'] < rsi_overbought:
                if current_row['close'] > current_row[f'BBU_{bbands_period}_{bbands_stddev:.1f}']:
                    buy_price = current_row['close']
                    highest_price_since_buy = buy_price
                    trailing_stop_price = highest_price_since_buy * (1 - trailing_stop_percent)
                    in_position = True
                    # Simulate the buy by calculating how many coins we could afford
                    coin_balance = equity / buy_price
                    equity = coin_balance * buy_price # Equity is now tied to the coin

        # Sell Logic
        elif in_position:
            if current_row['close'] > highest_price_since_buy:
                highest_price_since_buy = current_row['close']
                trailing_stop_price = highest_price_since_buy * (1 - trailing_stop_percent)

            if current_row['close'] <= trailing_stop_price:
                equity = (equity / buy_price) * current_row['close']
                in_position = False
            elif current_row['short_sma'] < current_row['long_sma'] and previous_row['short_sma'] >= previous_row['long_sma']:
                equity = (equity / buy_price) * current_row['close']
                in_position = False
    
    if in_position:
        equity = (equity / buy_price) * data.iloc[-1]['close']

    return equity

def main():
    """Main function to run the optimization process."""
    print(f"Fetching historical data for {SYMBOL_TO_TEST}...")
    historical_data = fetch_historical_data(SYMBOL_TO_TEST, TIMEFRAME, DATA_FETCH_LIMIT)
    if historical_data is None: return

    print("Data fetched. Generating strategy combinations...")

    param_grid = {
        'short_sma': SHORT_SMA_VALUES,
        'long_sma': LONG_SMA_VALUES,
        'rsi_overbought': RSI_OVERBOUGHT_VALUES,
        'bbands_period': BBANDS_PERIOD_VALUES,
        'bbands_stddev': BBANDS_STDDEV_VALUES,
        'trailing_stop': TRAILING_STOP_VALUES
    }
    keys, values = zip(*param_grid.items())
    
    all_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    valid_combinations = [p for p in all_combinations if p['short_sma'] < p['long_sma']]
    
    results = []
    
    print(f"Testing {len(valid_combinations)} different strategy combinations. This will take time...")

    for i, params in enumerate(valid_combinations):
        final_equity = run_single_backtest(historical_data.copy(), params)
        if final_equity > 0:
            results.append({
                'params': params,
                'final_equity': final_equity,
                'performance_%': ((final_equity / 1000.0) - 1) * 100
            })
        print(f"Tested combination {i+1}/{len(valid_combinations)} | Result: ${final_equity:.2f}")

    if not results:
        print("No valid results found.")
        return

    sorted_results = sorted(results, key=lambda x: x['final_equity'], reverse=True)

    print("\n--- Hedge Fund Optimization Complete ---")
    print(f"Top 5 performing strategies for {SYMBOL_TO_TEST} on the {TIMEFRAME} chart:")
    
    for i, result in enumerate(sorted_results[:5]):
        print(f"#{i+1}: Equity: ${result['final_equity']:.2f} | Perf: {result['performance_%']:.2f}% | Params: {result['params']}")

    best_strategy = sorted_results[0]['params']
    print("\n--- Recommendation ---")
    print("To make your live bot the 'best it can be', update 'main.py' with these settings:")
    print(f"SHORT_SMA_WINDOW = {best_strategy['short_sma']}")
    print(f"LONG_SMA_WINDOW = {best_strategy['long_sma']}")
    print(f"RSI_OVERBOUGHT = {best_strategy['rsi_overbought']}")
    print(f"BBANDS_PERIOD = {best_strategy['bbands_period']}")
    print(f"BBANDS_STDDEV = {best_strategy['bbands_stddev']}")
    print(f"TRAILING_STOP_PERCENT = {best_strategy['trailing_stop']}")

if __name__ == "__main__":
    main()
