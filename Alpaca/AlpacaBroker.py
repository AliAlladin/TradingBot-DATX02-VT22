from alpaca_trade_api import REST
import time
from Config import *


class AlpacaBroker:
    def __init__(self, symbols: list[str] = []):
        self.api = REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

    def get_balance(self):
        return float(self.api.get_account().cash)

    # Function that checks if market is open.
    def market_is_open(self):
        clock = self.api.get_clock()
        return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120

    def wait_for_market_open(self):
        clock = self.api.get_clock()
        if not clock.is_open:
            print("Going to sleep!")
            time_to_open = (clock.next_open - clock.timestamp).total_seconds()
            time.sleep(round(time_to_open))

    # Function to place a buy order.
    def buy(self, symbol: str, target_position_size: float, limit_price: float):
        returned = self.api.submit_order(
            symbol, target_position_size, "buy", "limit", "day", limit_price)
        print("BUY order for {} {} at {} {}".format(returned.qty,
              returned.symbol, returned.limit_pricem, returned.status))

    # Function to place a sell order.
    def sell(self, symbol: str, target_position_size: float, limit_price: float):
        returned = self.api.submit_order(
            symbol, target_position_size, "sell", "limit", "day", limit_price)
        print("SELL order for {} {} at {} {}".format(returned.qty,
              returned.symbol, returned.limit_pricem, returned.status))
