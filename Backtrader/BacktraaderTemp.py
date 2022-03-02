import datetime
import os
import sys  # To find out the script name (in argv[0])

import pandas as pd

pd.options.mode.chained_assignment = None

from Pair import *
from Strategies import *  # import our first strategy

# Instantiate Cerebro engine. This is the main control center / brain
cerebro = bt.Cerebro()

# Individual os paths
modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

# The data of pairs comes from Pairs.txt which we read
datap = os.path.join(modpath, 'Backtrader/Pairs.txt')
my_pair_file = open(datap, 'r')

# We start without any tickers
tickers = []  # A list of tickers
pairs = []  # A list of Pairs (see Pair.py)
dict = {}  # Dictionary to store tickers as keys and an integer value that separates the tickers.
i = 0  # A variable to work as a counter of the integer value

# We go through Pairs.txt to add all tickers and Pairs
for line in my_pair_file:
    stocks = line.split()
    stock1 = stocks[0]
    stock2 = stocks[1]
    pairs.append(Pair(stock1, stock2))

    # If the stock is not added into the list of tickers, we do it.
    if stock1 not in tickers:
        tickers.append(stock1)
        dict[stock1] = i
        i += 1
    if stock2 not in tickers:
        tickers.append(stock2)
        dict[stock2] = i
        i += 1


# Reformat txt-files to csv-files with added row for column names
def reformatData(input_path, output_path):
    df = pd.read_csv(input_path, sep=',', header=None)  # Creates a dataframe from txt-file, splits each row at ','

    header = ["DateTime", "Open", "High", "Low", "Close", "Volume"]  # Row for column names
    df.columns = header  # Adds column names to top of dataframe

    df.to_csv(output_path, index=False, )  # Converts dataframe to csv-file and saves file to Data/reformatted_csv_files


ticks = ['AAPL_1hour', 'AMZN_1hour']
# We add the data to cerebro
for ticker in ticks:
    txt_file_path = os.path.join(modpath, 'Data/txt_files/{}.txt').format(ticker)  # Full path to txt-file

    CSV_file_path = os.path.join(modpath, 'Data/reformatted_csv_files/{}.csv').format(ticker)  # Full path to csv-file

    reformatData(txt_file_path, CSV_file_path)  # Reformat txt-files to csv-files with added row for column names

    data = bt.feeds.GenericCSVData(

        dataname=CSV_file_path,  # Full path to csv-file
        fromdate=datetime.datetime(2021, 8, 2, 4, 00, 00),  # Ending  date
        todate=datetime.datetime(2021, 2, 13, 19, 59, 00),  # Starting date

        nullvalue=0.0,  # Used for replacing NaN-values with 0

        dtformat='%Y-%m-%d %H:%M:%S',  # used to parse the datetime CSV field. Default %Y-%m-%d
        tmformat='%H:%M:%S',  # used to parse the time CSV field if present

        datetime=0,  # column containing the date
        time=-1,  # column containing the time field if separate from the datetime field. -1 if not present.

        # For each below, reference the corresponding index from the data

        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,

        openinterest=-1  # -1 if no such column exists
    )
    cerebro.adddata(data)

# Set starting value of portfolio
cerebro.broker.setcash(100000.0)

# Add strategy to Cerebro
# TODO: allow for strategy switching
cerebro.addstrategy(Strategy_pairGen, dict, pairs)

# Set the commission - 0.1% ... divide by 100 to remove the %
cerebro.broker.setcommission(commission=0)

# Print starting portfolio value
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Creates csv files with inquired data. Has to be executed before cerebro.run()
# "out" specifies the name of the output file. It currently overwrites the same file.
cerebro.addwriter(bt.WriterFile, csv=True, out='log.csv')

# Core method to perform backtesting
cerebro.run()

# Print final portfolio value
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# To plot the trades
cerebro.plot()
