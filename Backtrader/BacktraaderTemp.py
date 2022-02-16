import os
import backtrader as bt
import backtrader.feeds as btfeed
import sys  # To find out the script name (in argv[0])
from Strategies import Strategy_1  # import our first strategy

# Instantiate Cerebro engine. This is the main control center / brain
cerebro = bt.Cerebro()

# Setting up path to data
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

# TODO: create generic data path reader
datapath = os.path.join(modpath, '../../TradingBot/Data/AMZN.csv')

# Create a Data Feed
# TODO: create generic data path reader
data = btfeed.YahooFinanceCSVData(dataname=datapath)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set starting value of portfolio
cerebro.broker.setcash(1000000)

# Add strategy to Cerebro
# TODO: allow for strategy switching
cerebro.addstrategy(Strategy_1)

# Print starting portfolio value
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Core method to perform backtesting
cerebro.run()

# Print final portfolio value
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
