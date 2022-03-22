import os
import sys

import pandas as pd
from Algorithms import PairsTrading


class Observer:
    def __init__(self, observable):
        observable.subscribe(self)

    def notify(
            self,
            observable,
            *args,
            **kwargs
    ):
        print('Got', args, kwargs)


if __name__ == "__main__":
    # NotificationBot.sendNotification("Last test")

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
    observer = Observer(strategy)

    strategy.run(latest_price, hist_data)
