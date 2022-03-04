import alpaca_trade_api as tradeapi
from Config import *
import time


class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

    def getBalance(self):
        return float(self.api.get_account().cash)

    # Function that checks if market is open.
    def market_is_open(self):
        clock = self.api.get_clock()
        return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120

    # Function that puts the program to sleep until the market opens.
    def wait_for_market_open(self):
        clock = self.api.get_clock()
        if not clock.is_open:
            time_to_open = (clock.next_open - clock.timestamp).total_seconds()
            time.sleep(round(time_to_open))


broker = Alpaca()
print(broker.api.get_account())
