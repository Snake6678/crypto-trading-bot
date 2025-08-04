# **Professional Crypto Trading & Analysis Bot**

This repository contains a sophisticated, multi-strategy cryptocurrency trading bot designed for market scanning, analysis, and automated execution. The system is built with a professional, object-oriented structure and includes advanced features for risk management and strategy optimization.

## **Core Features**

* **Dynamic Market Scanner:** Continuously scans the entire exchange (Binance.US) to find top-performing assets based on 24-hour volume and price change.  
* **Multi-Layered Strategy:** The bot's entry signals are based on a powerful combination of three distinct technical indicators for high-conviction trades:  
  * **Trend Following:** Uses a Simple Moving Average (SMA) Crossover to identify major trend shifts.  
  * **Momentum Confirmation:** Uses the Relative Strength Index (RSI) to avoid buying into overbought conditions.  
  * **Volatility Breakouts:** Uses Bollinger Bands to confirm that a move has strong momentum before entering.  
* **Advanced Risk Management:**  
  * **Trailing Stop-Loss:** A dynamic stop-loss that automatically moves up to lock in profits as a trade becomes more successful.  
  * **Dynamic Position Sizing:** Automatically adjusts the investment amount for each trade based on the asset's current market volatility (measured by ATR).  
* **Strategy Optimizer:** Includes a powerful backtesting script (optimizer.py) that can test hundreds of different strategy parameter combinations to find the most profitable settings for any given asset.

## **Technology Stack**

* **Language:** Python 3  
* **Core Libraries:**  
  * ccxt: For connecting to cryptocurrency exchanges.  
  * pandas: For data manipulation and analysis.  
  * pandas-ta: For calculating advanced technical indicators.

## **Setup & Installation**

1. **Clone the Repository:**  
   git clone \[https://github.com/snake6678/crypto-trading-bot.git\](https://github.com/snake6678/crypto-trading-bot.git)  
   cd crypto-trading-bot

2. **Install Dependencies:**  
   \# It is highly recommended to use a virtual environment  
   py \-m venv venv  
   .\\venv\\Scripts\\activate

   \# Install required packages  
   py \-m pip install \-r requirements.txt

3. Set API Keys:  
   This bot loads API keys from environment variables for security. Set them in your terminal session before running the bot.  
   set API\_KEY="YOUR\_BINANCE\_US\_API\_KEY"  
   set API\_SECRET="YOUR\_BINANCE\_US\_SECRET\_KEY"

## **Usage**

### **1\. Training the Bot (Optimization)**

Before running the live bot, use the optimizer to find the best strategy parameters for your desired asset and timeframe.

\# Edit optimizer.py to set the SYMBOL\_TO\_TEST  
py optimizer.py

The script will output the best-performing parameters. Update these in the config section of main.py.

### **2\. Running the Bot (Paper Trading)**

The bot is in paper trading (simulation) mode by default. To run it:

py main.py

The bot will start scanning the market and logging its decisions without placing real orders.

### **3\. Going Live**

**Warning:** Trading with real money is highly risky. Ensure you have completed thorough testing.

To enable live trading, you must edit the \_execute\_buy and \_execute\_sell functions in main.py by uncommenting the lines that place orders, as described in the code comments.

## **Disclaimer**

This software is for educational purposes only. Cryptocurrency trading is extremely risky and can result in significant financial loss. The author is not responsible for any losses incurred. Use at your own risk.
