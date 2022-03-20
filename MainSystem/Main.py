import os
import sys
from time import sleep
import pandas as pd
import PairsTrading
import AlpacaBroker
# from Database import handleData
from NotificationHandler import NotificationBot


class StrategyObserver:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self, observable, signal: dict):

        if signal['signal'] == "BUY":
            order_id = broker.buy(signal['symbol'], signal['volume'])
        elif signal['signal'] == "SELL":
            order_id = broker.sell(signal['symbol'], signal['volume'])
        
        # Wait for order to be filled:
        while broker.get_order(order_id)['filled_at'] is not None: 
            continue

        order = broker.get_order(order_id)
        # save order to database.
        # Send Slack-notification with order information.



def main():
    global broker
    broker = AlpacaBroker.AlpacaBroker()
    strategy = PairsTrading.PairsTrading()
    # data_provider = Data.YahooFinance()
    # database_handler = Database.PostgresSQL()

    observer = StrategyObserver(strategy)
    # dataObserver = DataObserver(data_provider)
    
    while True:
        if broker.market_is_open: # broker.market_is_open():
            # latest_price = database_handler.sqlLatest()
            # hist_data = data_provider.get_end_of_day(30)
            
            # Temporary test data --------------------------------------------------------------------------------------------------
            latest_price = pd.DataFrame({'Symbol': ['AMZN', 'AA', 'AAPL', 'A'], 'Price': [2837.06, 73.50, 150.62, 127.58]})
            hist_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/hist_data.csv'))
            # ----------------------------------------------------------------------------------------------------------------------
            
            strategy.run(latest_price, hist_data)
            sleep(60)
        else:
            # Send slack-notification at the end of the day with account balance and current positions.
            broker.wait_for_market_open()




if __name__ == "__main__":
    main()

    # #NotificationBot.sendNotification("Last test")

    # # These dataframes should be provided by the database, in the same format as below
    # # ----------------------------------------------------------------------------------------------------------------------
    # latest_price = pd.DataFrame({'Symbol': ['AMZN', 'AA', 'AAPL',
    #                             'A'], 'Price': [2837.06, 73.50, 150.62, 127.58]})

    # # Queried historical daily bar data
    # hist_data = pd.read_csv(os.path.join(os.path.dirname(
    #     os.path.dirname(sys.argv[0])), 'Data/hist_data.csv'))
    # # ----------------------------------------------------------------------------------------------------------------------

    # '''
    #     IF STRATEGY == PAIRSTRADING...
    # '''
    # # Initializing the subject/observable/strategy
    # strategy = PairsTrading.PairsTrading()

    # # Initializing the observer with the subject object
    # observer = StrategyObserver(strategy)

    # strategy.run(latest_price, hist_data)
