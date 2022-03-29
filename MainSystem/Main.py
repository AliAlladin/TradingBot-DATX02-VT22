from time import sleep
from Algorithms import PairsTrading
from Alpaca import AlpacaBroker
from MarketDataSocket import live_data_provider
from Database import handleData
from NotificationHandler import NotificationBot
import pandas as pd
import os
import sys
import test

class StrategyObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, observable, signal: dict):
        if signal['signal'] == "BUY":
            order_id = broker.buy(signal['symbol'], signal['volume'])   # Send buy order to broker
            while broker.get_order(order_id)['filled_at'] is not None:  # Wait for order to be filled
                continue

            handleData.sqlBuy(signal['symbol'], 0)  # TODO Get current price of ticker
        elif signal['signal'] == "SELL":
            order_id = broker.sell(signal['symbol'], signal['volume'])  # Send sell order to broker
            while broker.get_order(order_id)['filled_at'] is not None:  # Wait for order to be filled
                continue
            handleData.sqlSell(signal['symbol'], 0)  # TODO Get current price of ticker

        order = broker.get_order(order_id)
        message = "{} {} {} at {}".format(order['type'], order['symbol'], order['qty'], 0)  # TODO Get current price of ticker
        # NotificationBot.sendNotification(message)


class DataObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, observable, update):
        handleData.sqlUpdatePrice(stockTicker=update['ticker'], price=update['price'])


def main():
    pairs = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Backtrader/Pairs.txt'),
                        sep=" ",
                        header=None)

    pairs.columns = ['T1', 'T2']

    global broker
    broker = AlpacaBroker.AlpacaBroker()

    global strategy
    strategy = PairsTrading.PairsTrading(pairs, 0.5, 500, 10000)

    global data_provider
    data_provider = live_data_provider.liveDataStream(1, "pairs_data")
    data_provider.start()   # Start live-data thread

    strategy_observer = StrategyObserver(strategy)  # Add strategy observer
    dataObserver = DataObserver(data_provider)  # Add data observer

    tickers = set()
    for i in range(len(pairs.index)):
        tickers.add(pairs['T1'][i])
        tickers.add(pairs['T2'][i])

    hist_data = test.end_of_day(list(tickers), 30)

    while True:
        if broker.market_is_open():
            latest_price = handleData.sqlGetAllPrice()  # Get latest prices from database
            strategy.run(latest_price, hist_data)   # Run strategy
            sleep(60)   # Wait one minute
        else:
            # NotificationBot.sendNotification(broker.all_postions()) # Send notification of current positions and account valu
            live_data_provider.onClose()    # Lock live-data thread
            broker.wait_for_market_open()   # Send program to sleep until market opens.
            live_data_provider.marketOpen() # Unlock live-data thread
            hist_data = test.end_of_day(list(tickers), 30)  # Update historic data

if __name__ == "__main__":
    main()
