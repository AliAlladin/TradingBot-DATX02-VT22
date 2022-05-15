import os
import sys
from time import sleep

import pandas as pd

from Algorithms import PairsTrading
from Alpaca import AlpacaBroker
from DataProvider import live_data_provider, HistDataProvider
from Database import handleData
from NotificationHandler import NotificationBot


class StrategyObserver:
    """
    Observer-class for the strategy (observer pattern).
    """

    def __init__(self, observable):
        """
        Constructor for the class.
        :param observable: The object that is observable.
        """
        observable.subscribe(self)

    def notify(self, observable, signal: dict) -> None:
        """
        Sends the order to the broker, tells database_handler to save order information and tells NotificationBot to
        notify.
        :param observable: -
        :param signal: Dictionary with order information.
        :return:
        """
        try:
            if signal['signal'] == "BUY":
                order_id = broker.buy(signal['symbol'], (signal['volume']))  # Send buy order to broker
                if order_id is None:
                    return
                while broker.get_order(order_id)['filled_at'] is None:  # Wait for order to be filled
                    continue
                database_handler.sql_buy(signal['symbol'],
                                         database_handler.sql_get_price(signal['symbol']),
                                         round(broker.get_order(order_id)['qty']))
            elif signal['signal'] == "SELL":
                order_id = broker.sell(signal['symbol'], signal['volume'])  # Send sell order to broker
                if order_id is None:
                    return
                while broker.get_order(order_id)['filled_at'] is None:  # Wait for order to be filled
                    continue
                database_handler.sql_sell(signal['symbol'],
                                          database_handler.sql_get_price(signal['symbol']),
                                          round(broker.get_order(order_id)['qty']))

            order = broker.get_order(order_id)
            message = "{} {} {} at {}$".format(order['type'],
                                               order['qty'],
                                               order['symbol'],
                                               database_handler.sql_get_price(signal['symbol']))
            print(message)
            NotificationBot.sendNotification(message)

        except Exception as e:
            print(e)


class DataObserver:
    """
    Observer-class for the live data.
    """

    def __init__(self, observable):
        """
        Constructor for the class.
        :param observable: The object that is observable.
        """
        observable.subscribe(self)

    def notify(self, update) -> None:
        """
        Sends the latest stock price to the database_handler for it to save it.
        :param update: Dictionary with new price.
        :return: None
        """
        database_handler.sql_update_price(update['ticker'][0], update['price'][0])


def main() -> None:
    """
    Main method in which program runs.
    :return: None
    """
    pairs = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'MainSystem/Pairstorun.txt'),
                        sep=" ",
                        header=None)

    pairs.columns = ['t1', 't2']

    global broker
    broker = AlpacaBroker.AlpacaBroker()
    broker.get_shortable(pairs)

    global database_handler
    database_handler = handleData.DatabaseHandler()
    database_handler.sql_load_pairs(pairs)

    global strategy
    strategy = PairsTrading.PairsTrading(1, 50, 10000)

    global data_provider
    data_provider = live_data_provider.liveDataStream(1, "pairs_data", "../MainSystem/Pairstorun.txt")

    DataObserver(data_provider)  # Add data observer
    data_provider.start()  # Start live-data thread

    sleep(60)

    strategy_observer = StrategyObserver(strategy)  # Add strategy observer

    tickers = set()
    for i in range(len(pairs.index)):
        tickers.add(pairs['t1'][i])
        tickers.add(pairs['t2'][i])

    hist_data = HistDataProvider.end_of_day(list(tickers), 30)

    while True:
        if broker.market_is_open():
            try:
                print("Running")
                latest_price = database_handler.sql_get_all_prices()  # Get latest prices from database
                pairs = database_handler.sql_get_saved()
                strategy.run(pairs, latest_price, hist_data)  # Run strategy
                database_handler.sql_update_pairs(pairs)
                sleep(60)  # Wait one minute
            except Exception as e:
                print(e)
                continue
        else:
            try:
                NotificationBot.sendNotification("Portfolio value: {}".format(broker.get_portfolio_value()))
                NotificationBot.sendNotification("Going to sleep")
                live_data_provider.market_closed()  # Lock live-data thread
                broker.wait_for_market_open()  # Send program to sleep until market opens.
                NotificationBot.sendNotification("Starting")
                live_data_provider.market_open()  # Unlock live-data thread
                sleep(60)  # Wait one minute
                hist_data = HistDataProvider.end_of_day(list(tickers), 30)  # Update historic data
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()
