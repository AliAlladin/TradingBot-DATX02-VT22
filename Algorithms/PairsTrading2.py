import os
import sys  # To find out the script name (in argv[0])

import numpy as np
import statsmodels.api as sm
from IPython.display import display
import pandas as pd


class PairsTrading:
    def __init__(self, pairs: pd.DataFrame):
        self.pairs = pairs
        self.pairs['Active'] = False

        # The parameters that are to be varied to optimize the model
        self.distance = 3
        self.period = 500
        self.invested_amount = 10000
        self.trade_taken = False

    def run(self, lates_prices: pd.DataFrame, hist_prices: pd.DataFrame):
        print(self.pairs)
        for i in range(len(self.pairs.index)):
            # Fetches pair and their corresponding, updated prices from the dataframe provided by Main
            t1 = self.pairs['T1'][i]  # Ticker symbol
            t2 = self.pairs['T2'][i]  # Ticker symbol

            # Minute data for ticker
            tick1 = lates_prices.loc[lates_prices['Symbol'] == t1]
            # Minute data for ticker
            tick2 = lates_prices.loc[lates_prices['Symbol'] == t2]

            '''
            Creates a new dataframe with only the historical closing prices for the specific pair.
            By default, the Alpaca API will return today's candle even though it is not closed. This is incomplete.
            We update the last row later.
            '''
            data_df = pd.concat(
                [hist_prices[t1], hist_prices[t2]],
                axis=1,
                join='inner',
                keys=[t1, t2],
            )

            # Update the last row with the minute data
            data_df.iloc[-1] = [tick1.iat[0, 1], tick2.iat[0, 1]]

            # Perform a linear regression to calculate the spread
            result = sm.OLS(data_df[t1], data_df[t2]).fit()
            beta = result.params[0]
            spread = []

            for k in range(0, len(data_df)):
                spread.append(data_df[t1][k] - beta * data_df[t2][k])

            # Calculation of the Z-score
            mean = np.mean(spread)
            std = np.std(spread)
            z_score = (spread[len(data_df) - 1] - mean) / std

            # To know how much we need to buy of each stock
            shares_stock1 = self.invested_amount / \
                data_df[t1][len(data_df) - 1]
            current_ratio = data_df[t1][len(
                data_df) - 1] / data_df[t2][len(data_df) - 1]

            print(mean, std, z_score)


# ----------------------------------------------------------------------------------------------------------------------
# These dataframes should be provided by Main, in the same format as below
example_input = {'Symbol': ['AMZN', 'AA', 'AAPL',
                            'A'], 'Price': [2837.06, 73.50, 150.62, 127.58]}
latest_price = pd.DataFrame(example_input)

# Queried historical daily bar data
hist_data = pd.read_csv(os.path.join(os.path.dirname(
    os.path.dirname(sys.argv[0])), 'Algorithms/hist_data.csv'))

# Converting Pairs.txt to a dataframe
pairs = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Backtrader/Pairs.txt'), sep=" ",
                    header=None)

pairs.columns = ['T1', 'T2']
# ----------------------------------------------------------------------------------------------------------------------


strategy = PairsTrading(pairs)
strategy.run(latest_price, hist_data)
