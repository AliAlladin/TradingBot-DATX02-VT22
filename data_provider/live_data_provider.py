import datetime
import logging
import threading

import pandas as pd
import yliveticker

log = logging.getLogger(__name__)


class LiveDataStream(threading.Thread):
    """
    This class opens up a websocket on its own threat to yahoo! Finance and receives dataframes for each ticker
    requested for. Each ticker is received from the websocket, all the relevant information is extracted and then a
    notification is sent to all observers that new data can be gathered
    """

    def __init__(self, threadId, name, ticker_path):
        """
        Constructor for the class.
        :param threadId: Identification number of the thread starting the initialization.
        :param name: Name of the thread starting the initialization.
        :param ticker_path: path to a text file in which all tickers are written in.
        :return: None
        """

        threading.Thread.__init__(self)
        self.ticker_path = ticker_path
        self.threadID = threadId
        self.name = name
        self._observers = []

    def subscribe(self, observer):
        """
        Adds an observer to the list of observers.
        :param observer: Observer that should be attached to the observable.
        :return: None
        """
        self._observers.append(observer)

    def notify_observers(self, information):
        """
        Sends signal to all observers that new data can be gathered.
        :param information: The information that should be sent to observers.
        :return: None
        """
        for obs in self._observers:
            obs.notify(information)

    def unregister(self, observer):
        """
        Deletes an observer from the list of observers.
        :param observer: The observer that should be removed from observers.
        :return: None
        """
        self._observers.remove(observer)

    def run(self):
        """
        Starts the program and connects to the websocket.
        :return: None
        """
        global thisInstance
        thisInstance = self
        print('Starting ' + thisInstance.name + '\n')
        yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=extract_tickers(self.ticker_path))

    def open(self):
        yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=extract_tickers(self.ticker_path))


thisInstance = None

tickers = []

sleepLock = threading.Lock()
dataLock = threading.Lock()

savedData = list


def extract_tickers(ticker_path):
    """
    Method that extracts all tickers from a file in a filepath
    :param ticker_path: filepath in which all the tickers are located
    :return: list of all tickers that are on the file
    """
    # opening the file in read mode
    ticker_file = open(ticker_path, "r")
    # reading the file
    data = ticker_file.read()

    # replacing end of line('/n') with ' ' and
    # splitting the text it further when '.' is seen.
    data_into_list = data.replace('\n', ' ').split(" ")
    data_into_list.append('AZN')
    data_into_list.append('TLSNY')
    return data_into_list


def fix_time(timestamp):
    """
    Changes timestamp from a long sequence of numbers and makes it into normal time with year, month, day, hour, minute
    and second
    :param timestamp: a long sequence of numbers
    :return: time as a string with ear, month, day, hour, minute and second
    """
    stripped_time = int(str(timestamp)[:10])
    return datetime.datetime.fromtimestamp(stripped_time).strftime('%Y-%m-%d %H:%M:%S')


def send_data(data):
    """
    notifies all observers that new data can be gathered
    :param data: dataframe with data that can be gathered.
    :return: None
    """
    LiveDataStream.notify_observers(thisInstance, data)


def get_sp500_tickers():
    """
    Gets all tickers in the S&P 500 from a wikipedia list
    :return: A list will all the tickers in the S&P 500
    """
    payload = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = payload[0]
    df = first_table
    df.head()
    return df['Symbol'].values.tolist()


def save_data(data):
    """
    Saves data from websocket to a list that is thread safe
    :param data: dataframe with stock data
    :return: None
    """
    dataLock.acquire()
    global savedData
    savedData = data
    dataLock.release()


def access_live_data():
    """
    lets observers access data if needed in a thread safe way.
    :return: None
    """
    dataLock.acquire()
    return_data = savedData
    dataLock.release()
    return return_data


i = 0


def on_new_msg(ws, msg):
    """
    Everytime a new datapoint gets acquired by the websocket this method is run the dataframe is modified so that only
    ticker, price and timestamp os saved and then sent away so that the observers can be notified
    :param ws: Identification of what websocket is calling the method
    :param msg: A dataframe with stock data
    :return: None
    """
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
    else:
        sleepLock.acquire()
        sleepLock.release()


def market_closed():
    """
    if market is closed, this method is run to lock the main sequence
    :return: None
    """
    sleepLock.acquire()


def market_open():
    """
    if market is open, this method is run to start the main sequence
    :return: None
    """
    sleepLock.release()
    LiveDataStream.open(thisInstance)
