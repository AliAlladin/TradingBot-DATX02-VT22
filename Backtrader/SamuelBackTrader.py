import datetime
import os
import sys  # To find out the script name (in argv[0])
import pandas as pd
pd.options.mode.chained_assignment = None
from Pair import *
from samuelStrategy import *  # import our first strategy
def main():
    StrategyOne()
    #StrategyTwo()


def StrategyOne():
    strat='Strategy_pairGen'
    cerebro = bt.Cerebro() # Instantiate Cerebro engine. This is the main control center / brain

    modpath = os.path.dirname(os.path.dirname(sys.argv[0])) # Individual os paths

    datap = os.path.join(modpath, 'Backtrader/Pairs.txt') # The data of pairs comes from Pairs.txt which we read
    my_pair_file = open(datap, 'r')

    endValueForEachPair=[]

    
    # We go through Pairs.txt to add all tickers and Pairs
    for line in my_pair_file:
        pairs = []  # A list of Pairs (see Pair.py)
        stocks = line.split()
        cerebro = bt.Cerebro()
        pairs.append(Pair(stocks[0], stocks[1]))

        for ticker in stocks:
            add_data(ticker,cerebro)
        endValueForEachPair.append(run(cerebro,strat))
    total_portfolio_value=sum(endValueForEachPair)-len(endValueForEachPair)*100000
    print(total_portfolio_value)

def Strategy2():
    endValueForEachStock=[]
    strat='Strategy_fibonacci'
    my_stock_file = open('Stocks.txt', 'r')
    for stock in my_stock_file:
        cerebro = bt.Cerebro()
        add_data(cerebro, stock)
        endValueForEachStock.append(run(cerebro, strat))
    total_portfolio_value=sum(endValueForEachStock)-len(endValueForEachStock)*100000

def add_data(stock,cerebro):
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    CSV_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(stock)  # Full path to csv-file

    data = bt.feeds.GenericCSVData(

        dataname=CSV_file_path,  # Full path to csv-file
        fromdate=datetime.datetime(2015, 9, 1, 9, 30, 00),  # Start  date
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
        #compression=60

    )
    cerebro.adddata(data)


def creating_file_with_stocks():
    stocks = []
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    directory_in_str = os.path.join(modpath, 'Data/filtered_csv_data/')
    directory = os.fsencode(directory_in_str)
    for filename in os.listdir(directory):
        x = (str(filename))
        x = x.split('\'')[1]
        x = x.removesuffix('.csv')
        if "." in x:
            y = x.split('.')
            x = y[0] + "-" + y[1]
        stocks.append(x)
    my_pair_file = open('Stocks.txt', 'w')
    for i in stocks:  
        my_pair_file.write(i+ "\n")
    my_pair_file.close()

def run(cerebro, strat):
    cerebro.broker.setcash(100000.0)
    todate1=datetime.date(2019, 5, 1)
    cerebro.broker.setcommission(commission=0)  # Set the commission - 0.1% ... divide by 100 to remove the %
    if strat=='Strategy_pairGen':
        todate1=datetime.date(2019, 5, 1)
        cerebro.addstrategy(Strategy_pairGen, distance=1, period=500, invested=10000, todate=todate1,stock1='A', stock2='AA')
    else:
        cerebro.addstrategy(strat, distance=3, period=100, invested=100000, todate=todate1)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue()) # Print starting portfolio value

    # Creates csv files with inquired data. Has to be executed before cerebro.run()
    # "out" specifies the name of the output file. It currently overwrites the same file.
    cerebro.addwriter(bt.WriterFile, csv=True, out='log.csv')

    cerebro.run() # Core method to perform backtesting
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue()) # Print final portfolio value

    try: 
        cerebro.plot() # To plot the trades
    except IndexError:
        print('prob length 0')
    return cerebro.broker.getvalue()

main()
