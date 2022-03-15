import os
import sys  # To find out the script name (in argv[0])

import numpy as np
import statsmodels.api as sm
from IPython.display import display
import pandas as pd

'''
This class receives a dataframe containing the latest prices for each ticker.
It will go through each ticker, find its pair and perform the strategy on that pair in order
to check whether or not we should sell or buy a either of the stocks of that pair. In that case,
a sell/buy sigal will be passed back to Main. 
'''
# ----------------------------------------------------------------------------------------------------------------------
# These dataframes should be provided by Main, in the same format as below
example_input = {'Symbol': ['AMZN', 'AA', 'AAPL', 'A'], 'Price': [2837.06, 73.50, 150.62, 127.58]}
df = pd.DataFrame(example_input)

# Queried historical daily bar data
hist_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/hist_data.csv'))
# ----------------------------------------------------------------------------------------------------------------------

# Converting Pairs.txt to a dataframe
pairs = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Backtrader/Pairs.txt'), sep=" ",
                    header=None)
pairs.columns = ['T1', 'T2']

# The parameters that are to be varied to optimize the model
distance = 3
period = 500
invested_amount = 10000
trade_taken = False

# Iterate through all pairs
for i in range(len(pairs.index)):
    # Fetches pair and their corresponding, updated prices from the dataframe provided by Main
    t1 = pairs['T1'][i]  # Ticker symbol
    t2 = pairs['T2'][i]  # Ticker symbol

    tick1 = df.loc[df['Symbol'] == t1]  # Minute data for ticker
    tick2 = df.loc[df['Symbol'] == t2]  # Minute data for ticker

    '''
    Creates a new dataframe with only the historical closing prices for the specific pair.
    By default, the Alpaca API will return today's candle even though it is not closed. This is incomplete.
    We update the last row later.
    '''
    data_df = pd.concat(
        [hist_data[t1], hist_data[t2]],
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
    shares_stock1 = invested_amount / data_df[t1][len(data_df) - 1]
    current_ratio = data_df[t1][len(data_df) - 1] / data_df[t2][len(data_df) - 1]

    print(mean, std, z_score)

    # while not trade_taken:
    # print('Hello')
