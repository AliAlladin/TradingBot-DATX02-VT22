import os
import sys  # To find out the script name (in argv[0])
from MainSystem import Main
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import alpaca_trade_api as tradeapi
import pandas as pd
from alpaca_trade_api.rest import TimeFrame
from IPython.display import display

pd.options.display.max_columns = None

# The parameters that are to be varied to optimize the model
distance = 3
period = 25
invested_amount = 10000

# Individual os paths
modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
datap = os.path.join(modpath, 'Backtrader/Pairs.txt')

my_pair_df = pd.read_csv(datap, sep=" ")

# Connection
base_url = 'https://paper-api.alpaca.markets'
ALPACA_API_KEY = 'PKVIY9JARA7VQ6WC5M50'
data_url = 'wss://data.alpaca.markets'
ALPACA_SECRET_KEY = '5Y2d1GUGUhr8NWilj5vTZ1oB71ybC8eoRN6czMIh'
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url)
conn = tradeapi.stream.Stream(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url)
isActive = False
long_first_stock = False

t1 = my_pair_df.columns[0]  # Name of ticker
t2 = my_pair_df.columns[1]  # Name of ticker
t1_frame = api.get_bars(t1, TimeFrame.Day, "2020-09-30", "2020-11-03", adjustment='raw').df
t2_frame = api.get_bars(t2, TimeFrame.Day, "2020-09-30", "2020-11-03", adjustment='raw').df
data_df = pd.concat(
    [t1_frame.close, t2_frame.close],
    axis=1,
    join='inner',
    keys=[t1, t2],
)
# path = os.path.join(modpath, 'Algorithms/Hello.csv')
# ____.to_csv(path,index=False)

# Perform a linear regression to calculate the spread
result = sm.OLS(data_df[t1], data_df[t2]).fit()
beta = result.params[0]
spread = []
for i in range(0, period):
    spread.append(data_df[t1][i] - beta * data_df[t2][i])
spread_df = data_df.copy()
spread_df['spread'] = spread

mean = spread_df['spread'].mean()
std = spread_df['spread'].std()
z_score = (spread[period - 1] - mean) / std
print('Z: ' + str(z_score))
# To know how much we need to buy of each stock
shares_stock1 = invested_amount / data_df[t1][period - 1]
current_ratio = data_df[t1][period - 1] / data_df[t2][period - 1]

# If we don't have a position in this pair
if not isActive:
    # We check whether the Z-score is unusually high or low (>distance or <-distance)
    if z_score > distance:
        # High Z-score, we sell stock 1 and buy stock 2

        long_first_stock = False  # true when we are long of the first stock
        ratio = current_ratio
        shares_stock1 = shares_stock1
        trade_taken = True

        print('Strategy sent out sell signal')
        Main.buy_sell_signal = 'Sell'

    # The Z-score is unusually low, we buy stock1 and sell stock2
    elif z_score < distance:

        # Description of our position
        long_first_stock = True
        shares_stock1 = shares_stock1
        ratio = current_ratio
        isActive = True

        # buy stock1 and sell stock2
        print('Strategy sent out signal')

        signal = [{'B', t1}, {'S', t2}]
        Main.setSignal(signal)

# We have a position on a pair and therefore examine whether to close it
else:
    # We previously bought stock 1
    if long_first_stock:
        if z_score > 0:
            # Sell stock 1 and buy back stock 2
            signal = [{'S', t1}, {'B', t2}]
            Main.setSignal(signal)

            # We close the position in the pair
            isActive = False
            shares_stock1 = None
            ratio = None
    else:

        if z_score < 0:
            # Buy back stock 1 and sell stock 2
            signal = [{'B', t1}, {'S', t2}]
            Main.setSignal(signal)

            '''
            # Calculating the profit of the pairs trading
            profit = pair.shares_stock1 * pair.ratio * self.datas[self.dic.get(pair.stock2)] \
                     - pair.shares_stock1 * self.datas[self.dic.get(pair.stock1)]
            '''
            # We close the position in the pair
            isActive = False
            shares_stock1 = None
            ratio = None
