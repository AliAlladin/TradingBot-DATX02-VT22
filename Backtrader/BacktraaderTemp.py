import datetime
import os
import sys  # To find out the script name (in argv[0])

import pandas as pd

pd.options.mode.chained_assignment = None

from Strategies import *  # import our first strategy

# Instantiate Cerebro engine. This is the main control center / brain
cerebro = bt.Cerebro()

# Setting up path to data
modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

# tickers = ['AMZN', 'AAPL', 'NFLX']
# tickers = ['AAPL', 'AMZN','NFLX']
# tickers = ['NFLX', 'AMZN']
# tickers = ['AMZN_Nas', 'AAPL_Nas']
tickers = ['AMZN (1)', 'NFLX']

'''
for ticker in tickers:
    datapath = os.path.join(modpath, 'Data/{}.csv')
    file = datapath.format(ticker)
    data = bt.feeds.YahooFinanceCSVData(dataname=file)
    cerebro.adddata(data)  # Add the data to Cerebro
'''


# Used for reformatting data from Nasdaq. Run only once!
def reformatData(pathToFile):
    df = pd.read_csv(pathToFile)

    for i in range(len(df.index)):
        x = df['Date'][i]
        reformated_date = datetime.datetime.strptime(x, '%m/%d/%Y').strftime("%Y-%m-%d")
        df['Date'][i] = reformated_date

        x = df['Close/Last'][i]
        y = x.replace('$', '')
        df['Close/Last'][i] = y

        x = df['Open'][i]
        y = x.replace('$', '')
        df['Open'][i] = y

        x = df['High'][i]
        y = x.replace('$', '')
        df['High'][i] = y

        x = df['Low'][i]
        y = x.replace('$', '')
        df['Low'][i] = y

    df = df.iloc[::-1]  # Reverses order of dataframe
    df.to_csv(pathToFile, index=False, )


for ticker in tickers:
    datapath = os.path.join(modpath, 'Data/{}.csv')
    file = datapath.format(ticker)

    '''
    # Uncomment if you want to reformat the data. Should not be run more than once. 
    # reformatData(file)

    GenericCSVData() is used to parse different CSV formats. Below is for Nasdaq
    data = bt.feeds.GenericCSVData(
        dataname=file,
        fromdate=datetime.datetime(2017, 2, 28),  # Ending  date
        todate=datetime.datetime(2022, 2, 25),  # Starting date

        nullvalue=0.0,  # Used for replacing NaN-values with 0

        dtformat='%Y-%m-%d',  # used to parse the datetime CSV field. Default %Y-%m-%d
        tmformat='%H.%M.%S',  # used to parse the time CSV field if “present”

        datetime=0,  # column containing the date
        time=-1,  # column containing the time field if separate from the datetime field. -1 if not present.

        # For each below, reference the corresponding index from the data
        high=4,
        low=5,
        open=3,
        close=1,
        volume=2,
        openinterest=-1,  # -1 if no such column exists
    )
    
    # df = pd.read_csv(file)
    # df = df.iloc[::-1]  # Reverses order of dataframe
    # df.to_csv(file, index=False, )  # Overwrite csv file
    '''

    # Data feed for Yahoo
    data = bt.feeds.GenericCSVData(

        dataname=file,
        fromdate=datetime.datetime(2017, 2, 28),  # Ending  date
        todate=datetime.datetime(2022, 2, 25),  # Starting date

        nullvalue=0.0,  # Used for replacing NaN-values with 0

        dtformat='%Y-%m-%d',  # used to parse the datetime CSV field. Default %Y-%m-%d
        tmformat='%H.%M.%S',  # used to parse the time CSV field if “present”

        datetime=0,  # column containing the date
        time=-1,  # column containing the time field if separate from the datetime field. -1 if not present.

        # For each below, reference the corresponding index from the data
        high=2,
        low=3,
        open=1,
        close=4,
        volume=6,
        openinterest=-1,  # -1 if no such column exists
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
cerebro.plot()
