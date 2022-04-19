import datetime
import os
import random
import sys  # To find out the script name (in argv[0])

import pandas as pd

pd.options.mode.chained_assignment = None

from Pair import *
from Strategies import *  # import our Strategies


def main():
    StrategyOne()
    # StrategyTwo()


def StrategyOne():
    # Instantiate Cerebro engine. This is the main control center / brain
    cerebro = bt.Cerebro()

    # Individual os paths
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

    # The data of pairs comes from Pairs.txt which we read
    datap = os.path.join(modpath, 'Backtrader/Pairs.txt')
    my_pair_file = open(datap, 'r')
    endValueForEachPair = []
    # We go through Pairs.txt to add all tickers and Pairs
    for line in my_pair_file:
        pairs = []  # A list of Pairs (see Pair.py)
        tickers = []  # A list of tickers
        dict = {}  # Dictionary to store tickers as keys and an integer value that separates the tickers.
        i = 0  # A variable to work as a counter of the integer value
        stocks = line.split()
        cerebro = bt.Cerebro()
        pairs.append(Pair(stocks[0], stocks[1]))
        for ticker in stocks:
            dict[ticker] = i
            i = +1
            CSV_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(
                ticker)  # Full path to csv-file
            data = bt.feeds.GenericCSVData(
                dataname=CSV_file_path,  # Full path to csv-file
                fromdate=datetime.datetime(2017, 1, 1, 9, 30, 00),  # Start  date
                todate=datetime.datetime(2019, 1, 1, 16, 00, 00),  # Ending date

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
                # compression=60
            )
            cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)

        # Add strategy to Cerebro
        # TODO: allow for strategy switching
        todate1 = datetime.date(2019, 5, 1)
        cerebro.addstrategy(Strategy_pairGen, dic=dict, pairs=pairs, distance=3, period=100, invested=1000,
                            todate=todate1)

        # Set the commission - 0.1% ... divide by 100 to remove the %
        cerebro.broker.setcommission(commission=0)

        # Print starting portfolio value
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        print(pairs[0].get_pairs())

        # Creates csv files with inquired data. Has to be executed before cerebro.run()
        # "out" specifies the name of the output file. It currently overwrites the same file.
        cerebro.addwriter(bt.WriterFile, csv=True, out='log.csv')

        # Core method to perform backtesting
        cerebro.run()

        # Print final portfolio value
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

        # To plot the trades
        try:
            cerebro.plot()
        except IndexError:
            print('prob length 0')
        endValueForEachPair.append(cerebro.broker.getvalue())
    sum = 0
    for i in endValueForEachPair:
        sum += i - 100000
    print(endValueForEachPair)
    print(sum)


'''
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
'''
'''
    # We add the data to cerebro
    
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
    cerebro.plot()'''


def StrategyTwo():
    cerebro = bt.Cerebro()

    # Individual os paths
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

    # The data of pairs comes from Pairs.txt which we read
    datap = os.path.join(modpath, 'Backtrader/Fibo.txt')
    my_pair_file = open(datap, 'r')

    endValueForEachPair = []
    dic = {}
    dic['A'] = 0
    dic['AA'] = 1

    # We go through Pairs.txt to add all tickers and Pairs
    for line in my_pair_file:
        stock = line.split()[0]
        CSV_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(stock)  # Full path to csv-file
        data = bt.feeds.GenericCSVData(

            dataname=CSV_file_path,  # Full path to csv-file
            fromdate=datetime.datetime(2017, 1, 1, 9, 30, 00),  # Start  date
            todate=datetime.datetime(2019, 1, 1, 16, 00, 00),  # Ending date

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
            # compression=60

        )
        cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)

    # Add strategy to Cerebro
    # TODO: allow for strategy switching
    cerebro.addstrategy(Strategy_fibonacci2, dic=dic, period=60, invested=1000, max=60)

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
    try:
        cerebro.plot()
    except IndexError:
        print('prob length 0')
    endValueForEachPair.append(cerebro.broker.getvalue())
    sum = 0
    for i in endValueForEachPair:
        sum += i - 100000
    print(endValueForEachPair)
    print(sum)


def creating_file_with_stocks(start):
    priority_stocks = []
    not_priority_stocks = []
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
        datap = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(x)
        csv_file = open(datap, 'r')
        a = csv_file.readlines()[1]
        date = a.split()[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        priority = True
        if date > start:
            priority = False
        csv_file.close()

        if priority:
            priority_stocks.append(x)
        else:
            not_priority_stocks.append(x)

    stocks = random.shuffle(priority_stocks) + random.shuffle(not_priority_stocks)
    my_pair_file = open('Stocks.txt', 'w')
    for i in stocks:
        my_pair_file.write(i + "\n")
    my_pair_file.close()


# start=datetime.date(2013, 11, 1)
# creating_file_with_stocks()

main()
