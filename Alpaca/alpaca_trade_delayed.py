import numpy as np
import talib
import alpaca_trade_api as tradeapi
from Config import *
import time
from datetime import date, timedelta


api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY,
                    BASE_URL, api_version='v2')


def trade(symbol, data):
    positionSizing = 0.25

    timeList = []
    openList = []
    highList = []
    lowList = []
    closeList = []
    volumeList = []

    # Reads, formats and stores the new bars
    for bar in data:
        timeList.append(bar.t)
        openList.append(bar.o)
        highList.append(bar.h)
        lowList.append(bar.l)
        closeList.append(bar.c)
        volumeList.append(bar.v)

    # Processes all data into numpy arrays for use by talib
    timeList = np.array(timeList)
    openList = np.array(openList, dtype=np.float64)
    highList = np.array(highList, dtype=np.float64)
    lowList = np.array(lowList, dtype=np.float64)
    closeList = np.array(closeList, dtype=np.float64)
    volumeList = np.array(volumeList, dtype=np.float64)

    # Calculated trading indicators
    SMA20 = talib.SMA(closeList[-100:], 20)[-1]
    SMA50 = talib.SMA(closeList[-100:], 50)[-1]

    print("{} | SMA20: {} SMA50: {}".format(symbol, SMA20, SMA50))

    # Calculates the trading signals
    if SMA20 > SMA50:
        try:
            openPosition = api.get_position(symbol)
            print("Position already open")
        except tradeapi.rest.APIError:
            cashBalance = float(api.get_account().cash)
            price = closeList[-1]
            # Calculates required position size
            targetPositionSize = cashBalance / (price / positionSizing)
            # Market order to open position
            returned = api.submit_order(
                symbol, targetPositionSize, "buy", "market", "day")
            print("BOUGHT:")
            print(returned)

    else:
        try:
            # Closes position if SMA20 is below SMA50
            openPosition = api.get_position(symbol)
            # Market order to fully close position

            print(openPosition)

            returned = api.submit_order(
                symbol, openPosition.qty, "sell", "market", "day")
            print("SOLD:")
            print(returned)
        except tradeapi.rest.APIError:
            print("No open position")


def market_is_open():
    clock = api.get_clock()
    return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120


def wait_for_market_open():
    clock = api.get_clock()
    if not clock.is_open:
        time_to_open = (clock.next_open - clock.timestamp).total_seconds()
        time.sleep(round(time_to_open))


def main():
    assetsToTrade = ["SPY", "MSFT", "AAPL", "NFLX"]
    barTimeframe = tradeapi.TimeFrame.Minute  # 1H 1Min, 5Min, 15Min, 1H, 1D
    if market_is_open():
        while True:
            start_time = date.today().isoformat()
            current_time = api.get_clock().timestamp
            fifteen_minutes = timedelta(minutes=15)
            end_time = (current_time - fifteen_minutes).isoformat()
            for symbol in assetsToTrade:
                data = api.get_bars(symbol=symbol, start=start_time,
                                    end=end_time, timeframe=barTimeframe)
                trade(symbol=symbol, data=data)
            time.sleep(60)
            print("----------------------------------------")
    else:
        wait_for_market_open()


if __name__ == "__main__":
    main()
