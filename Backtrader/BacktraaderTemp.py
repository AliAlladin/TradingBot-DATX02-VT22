import os
import sys  # To find out the script name (in argv[0])

import backtrader as bt

from Strategies import Strategy_1  # import our first strategy

# Instantiate Cerebro engine. This is the main control center / brain
cerebro = bt.Cerebro()

# Setting up path to data
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))


# TODO: create generic data path reader
tickers = ['AMZN', 'AAPL']
for ticker in tickers:
    datapath = os.path.join(modpath, '../../TradingBot/Data/{}.csv')
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath.format(ticker))
    cerebro.adddata(data)  # Add the Data Feed to Cerebro

# Set starting value of portfolio
cerebro.broker.setcash(100000.0)

# Add strategy to Cerebro
# TODO: allow for strategy switching
cerebro.addstrategy(Strategy_1)

# Set the commission - 0.1% ... divide by 100 to remove the %
cerebro.broker.setcommission(commission=0.001)

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
