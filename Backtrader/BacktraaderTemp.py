import os
import sys  # To find out the script name (in argv[0])

import pandas as pd
from Strategies import *  # import our first strategy

pd.options.mode.chained_assignment = None


def main():
    strategy_one()
    strategy_two()


def strategy_one():
    # Individual os paths
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))

    # The data of pairs comes from Pairs.txt which we read
    datap = os.path.join(modpath, 'Backtrader/Pairs.txt')
    my_pair_file = open(datap, 'r')

    # A list of final values for each cerebro run
    final_values = []
    starting_cash = 100000.0

    # We go through Pairs.txt to add all tickers and Pairs
    for line in my_pair_file:
        pairs = []  # A list of Pairs (see Pair.py)
        dict = {}  # Dictionary to store tickers as keys and an integer value. {'TICKER' -> Integer}
        i = 0  # A variable to work as a counter of the integer value

        # Instantiate Cerebro engine. This is the main control center / brain
        cerebro = bt.Cerebro()

        # We append the pair to 'pairs' and the ticker with a unique value to 'dict'
        stocks = line.split()
        pairs.append(Pair(stocks[0], stocks[1]))
        for ticker in stocks:
            dict[ticker] = i
            i += 1

            # Full path to csv-file
            csv_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(ticker)

            # Format of the data
            data = bt.feeds.GenericCSVData(

                dataname=csv_file_path,  # Full path to csv-file
                fromdate=datetime.datetime(2017, 6, 2, 9, 30, 00),  # Start  date
                todate=datetime.datetime(2019, 6, 13, 16, 00, 00),  # Ending date

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
        cerebro.broker.setcash(starting_cash)

        # Add strategy to Cerebro
        todate1 = datetime.date(2019, 6, 13)  # The date for which we run the cerebro
        cerebro.addstrategy(Strategy_pairGen,
                            dic=dict,
                            pairs=pairs,
                            distance=2,
                            period=300,
                            invested=10000,
                            todate=todate1)

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

        # To plot the trades, with exception for when data does not exist on the interval
        try: 
            cerebro.plot()
        except IndexError:
            print('prob length 0')
        final_values.append(cerebro.broker.getvalue())

    # Calculate the total earned money for all of our cerebro runs
    total = sum(final_values) - len(final_values)*starting_cash

    print(total)


def strategy_two():
    print('hej')


main()
