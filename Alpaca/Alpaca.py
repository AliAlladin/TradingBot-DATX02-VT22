from alpaca_trade_api import REST, TimeFrame
from Config import *
import time
from datetime import date, datetime, timedelta


class Alpaca:
    def __init__(self):
        self.api = REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

    def get_balance(self):
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

    def get_intraday_data(self, symbol):
        current_time = self.api.get_clock().timestamp
        start_time = current_time.replace(hour=9, minute=30).isoformat()
        print(start_time)
        fifteen_minutes = timedelta(minutes=15)
        print(current_time)
        end_time = current_time.replace(hour=16, minute=00).isoformat()
        if self.market_is_open():
            end_time = (current_time - fifteen_minutes).isoformat()

        data = self.api.get_bars(symbol=symbol, start=start_time,
                                 end=end_time, timeframe=TimeFrame.Minute)

        return data.df


broker = Alpaca()

print(broker.get_intraday_data("AAPL"))
