from alpaca_trade_api import REST, TimeFrame, Stream
import threading
import time
import pandas as pd
from datetime import date, datetime, timedelta
from Config import *


class AlpacaData:
    def __init__(self, symbols: list[str] = []):
        self.api = REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
        self.stream = Stream(ALPACA_API_KEY,
                             ALPACA_SECRET_KEY,
                             BASE_URL,
                             data_feed='iex')
        self.stocks = symbols
        self.latest_prices = dict.fromkeys(symbols)
        if self.stocks:
            self.subscribe()

    # Function that checks if market is open.
    def market_is_open(self):
        clock = self.api.get_clock()
        return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120

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
        else:
            print("Market is closed")
            return

    # Function returns historical end-of-day stockdata
    def get_endofday_data(self, symbol: str, from_date: str):
        today = date.today()
        one_day = timedelta(days=1)
        end_date = (today - one_day)
        data = self.api.get_bars(symbol=symbol, start=from_date,
                                 end=end_date, timeframe=TimeFrame.Day)

        return data.df

    # ------------------ In progress ------------------ #
    async def get_live_bar(self, bar):
        self.latest_prices[bar.s] = bar.c

    def consumer_thread(self):
        self.stream.subscribe_quotes(self.get_live_bar, 'AAPL')
        global PREVIOUS
        PREVIOUS = "AAPL"
        self.stream.run()

    def subscribe(self):
        threading.Thread(target=self.consumer_thread.run_forever).start()
        time.sleep(5)  # give the initial connection time to be established
        while 1:
            for ticker in self.stocks:
                self.stream.unsubscribe_quotes(self.PREVIOUS)
                self.stream.subscribe_quotes(self.get_live_bar, ticker)
                self.PREVIOUS = ticker
            time.sleep(60)

    def add_live_bar(self, symbol: str):
        self.stocks.append(symbol)
        self.latest_prices[symbol] = 0
        self.stream.stop()
        self.subscribe()

    def delete_live_bar(self, symbol: str):
        self.stocks.remove(symbol)
        del self.latest_prices[symbol]
        self.stream.stop()
        self.subscribe()
    # ------------------------------------------------- #


data_provider = AlpacaData()
print(data_provider.get_endofday_data("MSFT", "2021-06-01"))
print(data_provider.get_intraday_data("AAPL"))
