# ==============================
# 📦 IMPORTS
# ==============================
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import schedule
import time
import os

# ==============================
# 🔐 API (FROM RAILWAY VARIABLES)
# ==============================
API_KEY = os.getenv("PKGKMB223GCOZ7ACJXAKENIAT3")
API_SECRET = os.getenv("BQhi6apfFv1HRZzNDwQbUuLdSACNStCye2mjbrLiYVn1")

trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# ==============================
# ⚙️ SETTINGS
# ==============================
WATCHLIST = ["AAPL", "TSLA", "MSFT"]

REFERENCE_CAPITAL = 100  # used to convert % → $

last_prices = {}

# ==============================
# 📊 GET PRICE
# ==============================
def get_price(symbol):
    request = StockLatestTradeRequest(symbol_or_symbols=symbol)
    trade = data_client.get_stock_latest_trade(request)
    return trade[symbol].price

# ==============================
# 💰 PLACE ORDER
# ==============================
def place_order(symbol, side, trade_value):
    price = get_price(symbol)
    qty = round(trade_value / price, 6)

    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.DAY
    )

    trading_client.submit_order(order)
    print(f"{side} {symbol} | ${trade_value:.2f}")

# ==============================
# 📈 STRATEGY
# ==============================
def check_and_trade(symbol):
    global last_prices

    current_price = get_price(symbol)

    # first run → store price
    if symbol not in last_prices:
        last_prices[symbol] = current_price
        print(f"Init {symbol}: {current_price}")
        return

    old_price = last_prices[symbol]

    percent_move = (current_price - old_price) / old_price

    print(f"{symbol}: {percent_move*100:.2f}%")

    # ignore very small moves (noise filter)
    if abs(percent_move) < 0.005:  # 0.5%
        return

    # convert % → $
    trade_value = abs(percent_move) * REFERENCE_CAPITAL

    # trading logic
    if percent_move > 0:
        place_order(symbol, OrderSide.SELL, trade_value)

    elif percent_move < 0:
        place_order(symbol, OrderSide.BUY, trade_value)

    # update last price
    last_prices[symbol] = current_price

# ==============================
# ⏰ RUN BOT
# ==============================
def run_bot():
    print("\n📊 Running scan...\n")
    for stock in WATCHLIST:
        check_and_trade(stock)

# run every 1 minute (for testing / live use)
schedule.every(1).minutes.do(run_bot)

# ==============================
# 🔁 MAIN LOOP
# ==============================
print("🤖 Bot started...")

while True:
    schedule.run_pending()
    time.sleep(60)
