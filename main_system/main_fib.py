import os
import sys
from time import sleep

import pandas as pd

from algorithms import fibonacci_trading
from alpaca import alpaca_broker_2
from data_provider import live_data_provider
from database import handle_data_fib
from notification_handler import notification_bot


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

    def notify(self, observable, signal: dict):
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
                print(database_handler.sql_get_price(signal['symbol']))
                database_handler.sql_sell(signal['symbol'],
                                          database_handler.sql_get_price(signal['symbol']),
                                          round(broker.get_order(order_id)['qty']))

            order = broker.get_order(order_id)
            message = "{} {} {} at {}$".format(order['type'],
                                               order['qty'],
                                               order['symbol'],
                                               database_handler.sql_get_price(signal['symbol']))
            print(message)
            notification_bot.send_notification('Fib: ' + message)

        except Exception as e:
            print(e)


class DataObserver:
    '''
    Observer-class for the live data.
    '''

    def __init__(self, observable):
        """
        Constructor for the class.
        :param observable: The object that is observable.
        """
        observable.subscribe(self)

    def notify(self, update):
        """
        Sends the latest stock price to the database_handler for it to save it.
        :param update: Dictionary with new price.
        :return: None
        """
        database_handler.sql_update_price(update['ticker'][0], update['price'][0])


def main():
    """
    Main method in which program runs.
    """

    pathToCSV = os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'main_system/final.csv')

    global broker
    broker = alpaca_broker_2.AlpacaBroker()

    global strategy
    strategy = fibonacci_trading.FibonacciStrategy(pathToCSV)

    global database_handler
    database_handler = handle_data_fib.DatabaseHandler()
    tickers = pd.read_csv('stocks_to_run.txt', header=None)
    ratios = pd.DataFrame(['0.382', '0.500', '0.618'])
    tickers.columns = ['ticker']
    tickers.sort_values(by='ticker', inplace=True)
    database_handler.sql_load_fib(ratios, tickers)
    database_handler.sql_load_investments(tickers)

    global data_provider
    data_provider = live_data_provider.LiveDataStream(2, "fib_data", "/stocks_to_run.txt")

    DataObserver(data_provider)  # Add data observer
    data_provider.start()  # Start live-data thread

    sleep(10)

    strategy_observer = StrategyObserver(strategy)  # Add strategy observer

    while True:
        if broker.market_is_open():
            print("Running")
            latest_price = database_handler.sql_get_all_prices()  # Get latest prices from database

            if len(latest_price) == 40:
                latest_price.drop(latest_price.index[latest_price['Symbol'] == 'TLSNY'], inplace=True)
                latest_price.drop(latest_price.index[latest_price['Symbol'] == 'AZN'], inplace=True)
                latest_price.reset_index(inplace=True, drop=True)
                dataFrame = database_handler.sql_get_saved()
                investments = database_handler.sql_get_investments()
                strategy.run(dataFrame, latest_price, investments)  # Run strategy
                database_handler.sql_update_fib(dataFrame)
                database_handler.sql_update_investments(investments)
                sleep(60)
            else:
                sleep(60)  # Wait one minute

        else:
            try:
                notification_bot.send_notification('Fib: ' + "Portfolio value: {}".format(broker.get_portfolio_value()))
                notification_bot.send_notification('Fib: ' + "Going to sleep")
                live_data_provider.market_closed()  # Lock live-data thread
                broker.wait_for_market_open()  # Send program to sleep until market opens.
                notification_bot.send_notification('Fib: ' + "Starting")
                live_data_provider.market_open()  # Unlock live-data thread
                sleep(60)  # Wait one minute
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()
