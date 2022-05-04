import os
import sys
from time import sleep

import pandas as pd

from Algorithms import FibonacciTrading
from Alpaca import AlpacaBroker2
from DataProvider import live_data_provider
from Database import handleDataFib
from NotificationHandler import NotificationBot

'''
Observer-class for the strategy (observer pattern).
'''
class StrategyObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    '''
    Sends the order to the broker, tells database_handler to save order information and tells NotificationBot to notify.
    '''
    def notify(self, observable, signal: dict):
        try:
            if signal['signal'] == "BUY":
                order_id = broker.buy(signal['symbol'], (signal['volume']))  # Send buy order to broker
                if order_id is None:
                    return
                while broker.get_order(order_id)['filled_at'] is None:  # Wait for order to be filled
                    continue
                database_handler.sqlBuy(signal['symbol'],
                                        database_handler.sqlGetPrice(signal['symbol']),
                                        round(broker.get_order(order_id)['qty']))
            elif signal['signal'] == "SELL":
                order_id = broker.sell(signal['symbol'], signal['volume'])  # Send sell order to broker
                if order_id is None:
                    return
                while broker.get_order(order_id)['filled_at'] is None:  # Wait for order to be filled
                    continue
                print(database_handler.sqlGetPrice(signal['symbol']))
                database_handler.sqlSell(signal['symbol'],
                                         database_handler.sqlGetPrice(signal['symbol']),
                                         round(broker.get_order(order_id)['qty']))

            order = broker.get_order(order_id)
            message = "{} {} {} at {}$".format(order['type'],
                                               order['qty'],
                                               order['symbol'],
                                               database_handler.sqlGetPrice(signal['symbol']))
            print(message)
            NotificationBot.sendNotification('Fib: ' + message)

        except Exception as e:
            print(e)

'''
Observer-class for the live data.
'''
class DataObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    '''
    Sends the latest stock price to the database_handler for it to save it. 
    '''
    def notify(self, update):
        database_handler.sqlUpdatePrice(update['ticker'][0], update['price'][0])

'''
main method in which program runs
'''
def main():

    pathToCSV = os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'MainSystem/final.csv')

    global broker
    broker = AlpacaBroker2.AlpacaBroker()

    global strategy
    strategy = FibonacciTrading.FibonacciStrategy(pathToCSV)

    global database_handler
    database_handler = handleDataFib.DatabaseHandler()
    tickers = pd.read_csv('Stockstorun.txt', header=None)
    ratios = pd.DataFrame(['0.382', '0.500', '0.618'])
    tickers.columns = ['ticker']
    tickers.sort_values(by='ticker', inplace=True)
    database_handler.sqlLoadFib(ratios, tickers)
    database_handler.sqlLoadInvestments(tickers)

    global data_provider
    data_provider = live_data_provider.liveDataStream(2, "fib_data", "../MainSystem/Stockstorun.txt")

    DataObserver(data_provider)  # Add data observer
    data_provider.start()  # Start live-data thread

    sleep(10)

    strategy_observer = StrategyObserver(strategy)  # Add strategy observer

    while True:
        if broker.market_is_open():
            print("Running")
            latest_price = database_handler.sqlGetAllPrices()  # Get latest prices from database

            if len(latest_price) == 40:
                latest_price.drop(latest_price.index[latest_price['Symbol'] == 'TLSNY'], inplace=True)
                latest_price.drop(latest_price.index[latest_price['Symbol'] == 'AZN'], inplace=True)
                latest_price.reset_index(inplace=True, drop=True)
                dataFrame = database_handler.sqlGetSaved()
                investments = database_handler.sqlGetInvestments()
                strategy.run(dataFrame, latest_price, investments)  # Run strategy
                database_handler.sqlUpdateFib(dataFrame)
                database_handler.sqlUpdateInvestments(investments)
                sleep(60)
            else:
                sleep(60)  # Wait one minute

        else:
            try:
                NotificationBot.sendNotification('Fib: ' + "Portfolio value: {}".format(broker.get_portfolio_value()))
                NotificationBot.sendNotification('Fib: ' + "Going to sleep")
                live_data_provider.marketClosed()  # Lock live-data thread
                broker.wait_for_market_open()  # Send program to sleep until market opens.
                NotificationBot.sendNotification('Fib: ' + "Starting")
                live_data_provider.marketOpen()  # Unlock live-data thread
                sleep(60)  # Wait one minute
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()
