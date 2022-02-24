import os
import sys  # To find out the script name (in argv[0])
from Pair import *
from Strategies import *  # import our first strategy

# Instantiate Cerebro engine. This is the main control center / brain
cerebro = bt.Cerebro()

# Setting up path to data
modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

# TODO: create generic data path reader

datap = os.path.join(modpath, 'Backtrader/Pairs.txt')
my_pair_file = open(datap, 'r')
tickers = []
dict = {}
i=0
pairs = []
for x in my_pair_file:
    stocks = x.split()
    stock1 = stocks[0]
    stock2 = stocks[1]
    pairs.append(Pair(stock1,stock2))
    if stock1 not in tickers:
        tickers.append(stock1)
        dict[stock1] = i
        i += 1
    if stock2 not in tickers:
        tickers.append(stock2)
        dict[stock2] = i
        i += 1


for ticker in tickers:
    datapath = os.path.join(modpath, 'Data/{}.csv')
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath.format(ticker))
    cerebro.adddata(data)  # Add the Data Feed to Cerebro
# Set starting value of portfolio
cerebro.broker.setcash(100000.0)

# Add strategy to Cerebro
# TODO: allow for strategy switching
cerebro.addstrategy(Strategy_pairGen,dict,pairs)

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
