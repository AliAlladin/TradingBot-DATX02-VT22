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

    # Function returns intraday stockdata (15-mintes delayed)
    def get_intraday_data(self, symbol: str):
        current_time = self.api.get_clock().timestamp
        start_time = current_time.replace(hour=9, minute=30).isoformat()
        fifteen_minutes = timedelta(minutes=15)
        end_time = current_time.replace(hour=16, minute=00).isoformat()

        if self.market_is_open():
            end_time = (current_time - fifteen_minutes).isoformat()

        data = self.api.get_bars(symbol=symbol, start=start_time,
                                 end=end_time, timeframe=TimeFrame.Minute)

        return data.df

    # Function returns historical end-of-day stockdata
    def get_endofday_data(self, symbol: str, from_date: str):
        today = date.today()
        one_day = timedelta(days=1)
        end_date = (today - one_day)
        data = self.api.get_bars(symbol=symbol, start=from_date,
                                 end=end_date, timeframe=TimeFrame.Day)

        return data.df

    # Function to place a buy order.
    def buy(self, symbol: str, target_position_size: float, limit_price: float):
        returned = self.api.submit_order(
            symbol, target_position_size, "buy", "limit", "day", limit_price)
        print("BUY order for {} {} at {} {}".format(returned.qty,
              returned.symbol, returned.limit_pricem, returned.status))

    # Function to place a sell order.
    def buy(self, symbol: str, target_position_size: float, limit_price: float):
        returned = self.api.submit_order(
            symbol, target_position_size, "sell", "limit", "day", limit_price)
        print("SELL order for {} {} at {} {}".format(returned.qty,
              returned.symbol, returned.limit_pricem, returned.status))
