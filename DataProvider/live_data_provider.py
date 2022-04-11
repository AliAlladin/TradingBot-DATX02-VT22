import datetime
import logging
import threading

import pandas as pd
import yliveticker

from NotificationHandler.NotificationBot import sendNotification

log = logging.getLogger(__name__)


# class that handles the creating of a new thread and sets up an observer
class liveDataStream(threading.Thread):
    def __init__(self, threadId, name, ticker_path):
        threading.Thread.__init__(self)
        self.ticker_path = ticker_path
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
        global thisInstance
        thisInstance = self
        print('Starting ' + thisInstance.name + '\n')
        yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=extractTickers(self.ticker_path), on_close=onClose, on_error=onError)



thisInstance = None

tickers = []

# lock that doesnt allow a thread to access a method if any other thread is active
sleepLock = threading.Lock()
dataLock = threading.Lock()

savedData = list


def extractTickers(ticker_path):
    # opening the file in read mode
    tickerFile = open(ticker_path, "r")
    # reading the file
    data = tickerFile.read()

    # replacing end of line('/n') with ' ' and
    # splitting the text it further when '.' is seen.
    data_into_list = data.replace('\n', ' ').split(" ")
    data_into_list.append('AZN')
    data_into_list.append('TLSNY')
    return data_into_list


# Function that take time from as a long sequence of numbers and makes it readable for normal people
def fix_time(timestamp):
    stripped_time = int(str(timestamp)[:10])
    return datetime.datetime.fromtimestamp(stripped_time).strftime('%Y-%m-%d %H:%M:%S')


# Function that gathers the live data for all the tickers in SP500
def send_data(data):
    liveDataStream.notify_observers(thisInstance, data)


# Function that gets the ticker for all the current S&P 500 companies from wikipedia.
def getSP500Tickers():
    payload = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = payload[0]
    df = first_table
    df.head()
    return df['Symbol'].values.tolist()


# Saves data from api to a list and notifies observers that new data is available
def save_data(data):
    dataLock.acquire()
    global savedData
    savedData = data
    dataLock.release()


# lets observers access data if needed in a thread safe way.
def accessLiveData():
    dataLock.acquire()
    returnData = savedData
    dataLock.release()
    return returnData


i = 0


# Everytime a new datapoint gets acquired by the websocket this method is run and sends it to its observers.
def on_new_msg(ws, msg):
    global i
    i += 1
    # This is locked, only when the market is closed
    if not sleepLock.locked():
        df = pd.DataFrame(
            data={
                'callNumber': [i],
                'ticker': [msg['id']],
                'price': [msg['price']],
                'timestamp': [fix_time(msg['timestamp'])]
            }
        )
        send_data(df)


       # print(df.T.to_string() + "\n")

    else:
        sleepLock.acquire()
        sleepLock.release()


# if market is closed, this method is run to lock the main sequence
def marketClosed():
    sendNotification('Live tracker going to sleep')
    sleepLock.acquire()


# if market is open, this method is run to start the main sequence
def marketOpen():
    sendNotification('Live tracker starting')
    sleepLock.release()


def onError(error):
    sendNotification('Yahoo live tracker crashed with message: ' + str(error))


def onClose():
    sendNotification('System Closed')


def main():
    thread1 = liveDataStream(1, 'thread1')
    thread1.start()
    # Remove join when called from other classes, just here for testing
    thread1.join()


if __name__ == "__main__":
    main()
