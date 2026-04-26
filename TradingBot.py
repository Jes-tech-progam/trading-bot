from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import schedule
import time

# ==============================
# 🔐 API
# ==============================
API_KEY = "PKGKMB223GCOZ7ACJXAKENIAT3"
API_SECRET = "BQhi6apfFv1HRZzNDwQbUuLdSACNStCye2mjbrLiYVn1"

trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# ==============================
# ⚙️ SETTINGS
# ==============================
WATCHLIST = ["AAPL", "TSLA", "MSFT"]

REFERENCE_CAPITAL = 100  # used to scale % → $
last_prices = {}

# ==============================
# 📊 PRICE
# ==============================
def get_price(symbol):
    request = StockLatestTradeRequest(symbol_or_symbols=symbol)
    trade = data_client.get_stock_latest_trade(request)
    return trade[symbol].price

# ==============================
# 💰 ORDER
# ==============================
def place_order(symbol, side, trade_value):
    price = get_price(symbol)
    qty = trade_value / price

    order = MarketOrderRequest(
        symbol=symbol,
        qty=round(qty, 2),
        side=side,
        time_in_force=TimeInForce.DAY
    )

    trading_client.submit_order(order)
    print(f"{side} {symbol} | ${trade_value:.2f}")

# ==============================
# 📈 STRATEGY (PERCENT = MONEY)
# ==============================
def check_and_trade(symbol):
    global last_prices

    current_price = get_price(symbol)

    if symbol not in last_prices:
        last_prices[symbol] = current_price
        return

    old_price = last_prices[symbol]

    percent_move = (current_price - old_price) / old_price

    # convert percent → dollar trade size
if abs(percent_move) < 0.005:  # ignore small moves
    return

trade_value = abs(percent_move) * REFERENCE_CAPITAL

    if percent_move > 0:
        place_order(symbol, OrderSide.SELL, trade_value)

    elif percent_move < 0:
        place_order(symbol, OrderSide.BUY, trade_value)

    last_prices[symbol] = current_price

# ==============================
# ⏰ WEEKLY RUN
# ==============================
def run_bot():
    print("Running weekly scan...")
    for stock in WATCHLIST:
        check_and_trade(stock)

schedule.every().monday.at("09:00").do(run_bot)

# ==============================
# 🔁 LOOP
# ==============================
print("Bot running...")

while True:
    schedule.run_pending()
    time.sleep(60)
