import datetime
import os
import sys  # To find out the script name (in argv[0])

import pandas as pd

pd.options.mode.chained_assignment = None

from Strategies import *

# Instantiate Cerebro engine. This is the main control center / brain
cerebro = bt.Cerebro()

# Setting up path to data
modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

# tickers = ['AMZN', 'AAPL', 'NFLX']
# tickers = ['AAPL', 'AMZN','NFLX']
# tickers = ['NFLX', 'AMZN']
# tickers = ['AMZN_Nas', 'AAPL_Nas']
# tickers = ['AMZN (1)', 'NFLX']
tickers = ['AAPL_1min', 'AMZN_1min']

'''
for ticker in tickers:
    datapath = os.path.join(modpath, 'Data/{}.csv')
    file = datapath.format(ticker)
    data = bt.feeds.YahooFinanceCSVData(dataname=file)
    cerebro.adddata(data)  # Add the data to Cerebro
'''


# Used for reformatting data from Nasdaq. Run only once!
def reformatData(pathToFile, outputName):
    cs = os.path.join(modpath, 'Data/{}')  # Holder

    df = pd.read_csv(pathToFile, sep=',', header=None)

    header = ["DateTime", "Open", "High", "Low", "Close", "Volume"]
    df.columns = header

    new = cs.format(outputName)

    df.to_csv(new, index=False, )


for ticker in tickers:
    datapath = os.path.join(modpath, 'Data/{}.txt')  # Holder
    file = datapath.format(ticker)  # Path to file, example Data/AAPL.txt

    csvPath = os.path.join(modpath, 'Data/{}.csv')  # Holder
    csvFile = csvPath.format(ticker)  # Path to file, example Data/AAPL.csv

    i = '{}.csv'  # Holder
    fileName = i.format(ticker)  # Example, AAPL.csv

    # Converts txt files to CSV-files with added header
    reformatData(file, fileName)

    data = bt.feeds.GenericCSVData(

        dataname=csvFile,
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
cerebro.addstrategy(Strategy_pair)

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

"""
Requires matplotlib==3.2.2. Run the following in order to execute:
pip uninstall matplotlib
pip install matplotlib==3.2.2
"""
# cerebro.plot()
