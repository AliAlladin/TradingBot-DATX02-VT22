import datetime
import os
import sys  # To find out the script name (in argv[0])
import backtrader as bt
import backtrader.analyzers as btanalyzers
#import qgrid
import time

import pandas as pd

pd.options.mode.chained_assignment = None

from Pair import *
from optimizeStrats import *  # import our first strategy

#runstrat = 'fib'
runstrat = 'pair'
tic = time.perf_counter()

#startcash
startcash = 100000.0

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



# We add the data to cerebro
for ticker in tickers:

    CSV_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(ticker)  # Full path to csv-file

    data = bt.feeds.GenericCSVData(

        dataname=CSV_file_path,  # Full path to csv-file
        fromdate=datetime.datetime(2017, 4, 1, 9, 30, 00),  # Start  date
        todate=datetime.datetime(2019, 5, 1, 16, 00, 00),  # Ending date

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

        openinterest=-1,  # -1 if no such column exists
        timeframe=bt.TimeFrame.Minutes,
        compression=60

    )
    cerebro.adddata(data)

# Set starting value of portfolio
cerebro.broker.setcash(startcash)

if runstrat == 'pair':

    # Add strategy to Cerebro
    # TODO: allow for strategy switching
    #end date to know when to close positions
    todate1 = datetime.date(2019, 5, 1)
    dis = np.linspace(0.5, 3.0, num=2)
    per = range(100,200,100)
    max = max(per)
    strats = cerebro.optstrategy(Strategy_pairGen, todate = todate1, distance= dis, period=per, maximum = max,invested=100000)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0)

    # Print starting portfolio value
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Creates csv files with inquired data. Has to be executed before cerebro.run()
    # "out" specifies the name of the output file. It currently overwrites the same file.
    #cerebro.addwriter(bt.WriterFile, csv=True, out='log.csv')

    # Core method to perform backtesting

    # Print final portfolio value

    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(btanalyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(btanalyzers.Returns, _name="returns")

    back = cerebro.run(maxcpus = 1)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


    par_list = [[x[0].params.distance,
                 x[0].params.period,
                 x[0].analyzers.returns.get_analysis()['rtot'],
                 x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                 x[0].analyzers.sharpe.get_analysis()['sharperatio']
                ] for x in back]
    par_df = pd.DataFrame(par_list, columns = ['distance', 'period', 'return', 'dd', 'sharpe'])
    #qgrid.show_grid(par_df)

else:
    per = range(4000, 10000, 3000)
    max = max(per)
    strats = cerebro.optstrategy(Strategy_fibonacci2, invested=15000, period=per,maximum = max)

    cerebro.broker.setcommission(commission=0)

    # Print starting portfolio value
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Creates csv files with inquired data. Has to be executed before cerebro.run()
    # "out" specifies the name of the output file. It currently overwrites the same file.
    # cerebro.addwriter(bt.WriterFile, csv=True, out='log.csv')

    # Core method to perform backtesting

    # Print final portfolio value

    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(btanalyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(btanalyzers.Returns, _name="returns")

    back = cerebro.run(maxcpus=1)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    par_list = [[x[0].params.period,
                 x[0].analyzers.returns.get_analysis()['rtot'],
                 x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                 x[0].analyzers.sharpe.get_analysis()['sharperatio']
                 ] for x in back]
    par_df = pd.DataFrame(par_list, columns=['period', 'return', 'dd', 'sharpe'])
    # qgrid.show_grid(par_df)
print(par_df)
toc = time.perf_counter()
print('running optimize took ' , toc-tic , 'seconds')

# To plot the trades
#cerebro.plot()