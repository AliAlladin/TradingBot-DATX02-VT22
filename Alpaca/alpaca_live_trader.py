import numpy
import numpy as np
import talib
import alpaca_trade_api as tradeapi
from Config import *
import time
from datapackage import Package
import pandas

from datetime import date, timedelta

import logging
from alpaca_trade_api.stream import Stream

log = logging.getLogger(__name__)
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY,
                    BASE_URL, api_version='v2')

positionSizing = 0.25


# Save intraday data to a list.


def save_data(list, price):
    list.append(price)
    if len(list) > 100:
        list.pop(0)


saved_prices = []


# Function that take the bar of the share that wants to be traded.


async def trade(bar):
    print('im here')
    if market_is_open():

        save_data(saved_prices, bar.close)
        # Check if enough data:
        if len(saved_prices) == 100:
            close_list = np.array(saved_prices, dtype=np.float64)
            # Calculates 50-period exponential moving average.
            EMA50 = talib.EMA(close_list, 100)[-1]
            print("{} | Closing price: {} EMA50: {}".format(
                bar.symbol, bar.close, EMA50))

            # Calculates the trading signals and buy:
            if bar.close > EMA50:
                try:
                    openPosition = api.get_position(bar.symbol)
                    print("Position already open")
                except tradeapi.rest.APIError:
                    cashBalance = float(api.get_account().cash)
                    price = bar.close
                    # Calculates required position size
                    targetPositionSize = cashBalance / (price / positionSizing)
                    # Market order to open position
                    returned = api.submit_order(
                        bar.symbol, targetPositionSize, "buy", "market", "day")
                    print("BOUGHT:")
                    print(returned)
            else:
                # Check if position is open and close position if SMA20 is below SMA50
                try:
                    # Closes position if price is below EMA50

                    openPosition = api.get_position(bar.symbol)
                    # Market order to fully close position
                    print(openPosition)

                    returned = api.submit_order(
                        bar.symbol, openPosition.qty, "sell", "market", "day")
                    print("SOLD:")
                    print(returned)
                except tradeapi.rest.APIError:
                    print("No open position")
        # Else collect data:
        else:
            print(bar)
            print("Collecting data {}/100".format(len(saved_prices)))


    else:
        wait_for_market_open()


# Function that checks if market is open.


def market_is_open():
    clock = api.get_clock()
    return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120


# Function that puts the program to sleep until the market opens.


def wait_for_market_open():
    clock = api.get_clock()
    if not clock.is_open:
        print("Going to sleep!")
        time_to_open = (clock.next_open - clock.timestamp).total_seconds()
        time.sleep(round(time_to_open))


# Main program loop.


def getSP500Tickers():
    payload = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = payload[0]
    df = first_table
    df.head()
    return df['Symbol'].values.tolist()


def main():
    logging.basicConfig(level=logging.INFO)

    stream = Stream(ALPACA_API_KEY,
                    ALPACA_SECRET_KEY,
                    BASE_URL,
                    data_feed='iex')

    tickers = getSP500Tickers()

    for ticker in tickers:
        stream.subscribe_bars(trade, ticker)

    print('lolololololo')
    stream.run()


if __name__ == "__main__":
    main()
