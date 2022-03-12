import numpy
import numpy as np
import talib
import alpaca_trade_api as tradeapi
from Config import *
import time
import pandas as pd
import datetime
import threading
import logging
from alpaca_trade_api.stream import Stream

log = logging.getLogger(__name__)
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY,
                    BASE_URL, api_version='v2')


# class that handles the creating of a new thread and sets up an observer
class alpacaLiveDataStream(threading.Thread):
    def __init__(self, threadId, name):
        threading.Thread.__init__(self)
        self.threadID = threadId
        self.name = name
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, information):
        for obs in self._observers:
            obs.notify(information)

    def unregister(self, observer):
        self._observers.remove(observer)

    def run(self):
        print('Starting' + self.name + '\n')

        logging.basicConfig(level=logging.INFO)
        stream = Stream(ALPACA_API_KEY,
                        ALPACA_SECRET_KEY,
                        BASE_URL,
                        data_feed='iex')

        tickers = getSP500Tickers()

        for ticker in tickers:
            stream.subscribe_bars(getLiveData, ticker)

        stream.run()


# lock that doesnt allow a thread to access a method if any other thread is active
lock = threading.Lock()

savedData = list
saved_prices = []


# Function that take time from alpaca api and makes it readable for normal people
def fix_time(bar):
    stripped_time = int(str(bar.timestamp)[:10])
    return datetime.fromtimestamp(stripped_time).strftime('%Y-%m-%d %H:%M:%S')


# Function that gathers the live data for all the tickers in SP500
def send_data(data):
    alpacaLiveDataStream.notify_observers(data)


async def getLiveData(bar):
    print('im here')
    if market_is_open():

        fixedTime = fix_time(bar)
        save_data(bar)
        send_data(bar)
        print(bar)

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


# Function that gets the ticker for all the current S&P 500 companies from wikipedia.
def getSP500Tickers():
    payload = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = payload[0]
    df = first_table
    df.head()
    return df['Symbol'].values.tolist()


# Saves data from api to a list and notifies observers that new data is available
def save_data(data):
    lock.acquire()
    global savedData
    savedData = data
    lock.release()


# lets observers access data if needed in a thread safe way.
def accessLiveData():
    lock.acquire()
    returnData = savedData
    lock.release()
    return returnData


def main():
    thread1 = alpacaLiveDataStream(1, 'thread1')
    thread1.start()
    # Remove join when called from other classes, just here for testing
    thread1.join()


if __name__ == "__main__":
    main()
