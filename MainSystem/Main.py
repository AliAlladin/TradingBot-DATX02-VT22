from time import sleep
from Algorithms import PairsTrading
from Alpaca import AlpacaBroker
from DataProvider import live_data_provider, hist_data_provider
from Database import handleData
from NotificationHandler import NotificationBot
import pandas as pd
import os
import sys


class StrategyObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, observable, signal: dict):
        try:
            if signal['signal'] == "BUY":
                order_id = broker.buy(signal['symbol'], (signal['volume'])) # Send buy order to broker
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
                database_handler.sqlSell(signal['symbol'],
                                         database_handler.sqlGetPrice(signal['symbol']),
                                         round(broker.get_order(order_id)['qty']))

            order = broker.get_order(order_id)
            message = "{} {} {} at {}$".format(order['type'],
                                              order['qty'],
                                              order['symbol'],
                                              database_handler.sqlGetPrice(signal['symbol']))
            print(message)
            #NotificationBot.sendNotification(message)

        except Exception as e:
            print(e)

class DataObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, update):
        database_handler.sqlUpdatePrice(update['ticker'][0], update['price'][0])


def main():

    pairs = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Backtrader/Pairs.txt'),
                        sep=" ",
                        header=None)


    pairs.columns = ['T1', 'T2']

    global broker
    broker = AlpacaBroker.AlpacaBroker()

    global strategy
    strategy = PairsTrading.PairsTrading(pairs, 2, 600, 1000)

    global database_handler
    database_handler = handleData.DatabaseHandler()

    global data_provider
    data_provider = live_data_provider.liveDataStream(1, "pairs_data")

    broker.get_shortable(pairs)

    DataObserver(data_provider)  # Add data observer
    data_provider.start()   # Start live-data thread

    sleep(60)

    strategy_observer = StrategyObserver(strategy)  # Add strategy observer

    tickers = set()
    for i in range(len(pairs.index)):
        tickers.add(pairs['T1'][i])
        tickers.add(pairs['T2'][i])

    hist_data = hist_data_provider.end_of_day(list(tickers), 30)

    while True:
        if broker.market_is_open():
            try:
                print("Running")
                latest_price = database_handler.sqlGetAllPrices()  # Get latest prices from database
                strategy.run(latest_price, hist_data)  # Run strategy
                sleep(60)  # Wait one minute
            except Exception as e:
                print(e)
                continue
        else:
            try:
                NotificationBot.sendNotification("Portfolio value: {}".format(broker.get_portfolio_value()))
                NotificationBot.sendNotification("Going to sleep")
                live_data_provider.marketClosed()  # Lock live-data thread
                broker.wait_for_market_open()  # Send program to sleep until market opens.
                NotificationBot.sendNotification("Starting")
                live_data_provider.marketOpen()  # Unlock live-data thread
                sleep(60)  # Wait one minute
                hist_data = hist_data_provider.end_of_day(list(tickers), 30)  # Update historic data
            except Exception as e:
                print(e)

if __name__ == "__main__":
    main()
