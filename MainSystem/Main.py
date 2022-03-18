import os
import sys
from time import sleep
import pandas as pd
from Algorithms import PairsTrading
# from Alpaca import AlpacaBroker
# from Database import handleData
# from NotificationHandler import NotificationBot


class StrategyObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, observable, signal: dict):
        print(signal)
        



# def main():
    # strategy = PairsTrading.PairsTrading()
    # broker = AlpacaBroker.AlpacaBroker()
    # data_provider = Data.YahooFinance()
    # database_handler = Data.PostgresSQL()

    # signalObserver = Observer(strategy)
    # dataObserver = Observer(data_provider)
    
    # while True:
    #     if broker.market_is_open():
    #         # Do stuff
    #         latest_price = database_handler.sqlLatest()
    #         hist_data = data_provider.get_end_of_day(30)
    #         strategy.run(latest_price, hist_data)
    #         sleep(60)
    #     else:
    #         broker.wait_for_market_open()




if __name__ == "__main__":
    # main()

    #NotificationBot.sendNotification("Last test")

    # These dataframes should be provided by the database, in the same format as below
    # ----------------------------------------------------------------------------------------------------------------------
    example_input = {'Symbol': ['AMZN', 'AA', 'AAPL',
                                'A'], 'Price': [2837.06, 73.50, 150.62, 127.58]}
    latest_price = pd.DataFrame(example_input)

    # Queried historical daily bar data
    hist_data = pd.read_csv(os.path.join(os.path.dirname(
        os.path.dirname(sys.argv[0])), 'Data/hist_data.csv'))
    # ----------------------------------------------------------------------------------------------------------------------

    '''
        IF STRATEGY == PAIRSTRADING...
    '''
    # Initializing the subject/observable/strategy
    strategy = PairsTrading.PairsTrading()

    # Initializing the observer with the subject object
    observer = StrategyObserver(strategy)

    strategy.run(latest_price, hist_data)
