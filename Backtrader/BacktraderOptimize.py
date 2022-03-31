from optimizeStrats import *  # import our first strategy
import os
import sys  # To find out the script name (in argv[0])
import backtrader.analyzers as btanalyzers
import time

import pandas as pd

pd.options.mode.chained_assignment = None


def run_optimize(strategy):

    tic = time.perf_counter()

    cerebro = bt.Cerebro()  # Instantiate Cerebro engine. This is the main control center/brain
    starting_budget = 100000.0  # The amount of money we start with in the optimization
    # Set starting value of portfolio
    cerebro.broker.setcash(starting_budget)

    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))  # Individual os paths

    # We run optimize for the Pair trading strategy
    if strategy == 'Pair':
        tickers = get_tickers_from_pairs(modpath)  # We add the tickers (ONCE!) from all pairs

    # We run optimize for the Fibonacci retracement strategy
    else:
        tickers = get_tickers_from_stocks(modpath)  # We add all the tickers

    # We add the data for all tickers
    add_data(cerebro, modpath, tickers)
    cerebro.broker.setcommission(commission=0)  # We do not have any commission
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())  # Starting portfolio value

    if strategy == 'Pair':
        # The values of what we want to run the strategy for
        last_date = datetime.date(2019, 1, 5)   # Last date to know when to close positions
        distance = np.linspace(2, 3, num=5)     # Decides when to buy or sell
        period = np.linspace(450, 650, num=4)   # For how long time in the path we look for deviations
        maximum = max(period)                   # The maximum period, to make sure all runs starts at the same date
        invested_amount = 10000                 # The amount we invest in each pair

        optimize_pair(cerebro, last_date, distance, period, maximum, invested_amount)

    else:
        period = range(10, 100, 15)
        maximum = max(period)
        strats = cerebro.optstrategy(Strategy_fibonacci2, invested=1000, period=period, maximum=maximum)


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
    print('running optimize took ', toc-tic, 'seconds')


def add_data(cerebro, modpath, tickers):
    # We add the data to cerebro
    for ticker in tickers:
        csv_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(ticker)  # Full path to csv-file

        data = bt.feeds.GenericCSVData(

            dataname=csv_file_path,  # Full path to csv-file
            fromdate=datetime.datetime(2013, 9, 5, 9, 30, 00),  # Start  date
            todate=datetime.datetime(2016, 1, 7, 16, 00, 00),  # Ending date

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
            # compression=1

        )
        cerebro.adddata(data)


def get_tickers_from_pairs(path):
    # The data of pairs comes from Pairs.txt which we read
    data_path = os.path.join(path, 'Backtrader/Pairs.txt')
    my_pair_file = open(data_path, 'r')

    tickers = []  # A list of tickers

    # We go through Pairs.txt to add all tickers and Pairs
    for line in my_pair_file:
        stocks = line.split()
        stock1, stock2 = stocks[0], stocks[1]

        # If the stock is not added into the list of tickers, we do it.
        if stock1 not in tickers:
            tickers.append(stock1)

        if stock2 not in tickers:
            tickers.append(stock2)
    my_pair_file.close()

    return tickers


def get_tickers_from_stocks(path):
    # The data of pairs comes from Pairs.txt which we read
    data_path = os.path.join(path, 'Backtrader/Pairs.txt')
    my_stock_file = open(data_path, 'r')
    tickers = []
    for stock in my_stock_file:
        tickers.append(stock)
    my_stock_file.close()

    return tickers


def optimize_pair(cerebro, last, dist, per, maxi, amount):

    strats = cerebro.optstrategy(Strategy_pairGen,
                                 todate=last,
                                 distance=dist,
                                 period=per,
                                 maximum=maxi,
                                 invested=amount)

    # TODO: Remove this?
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

    par_list = [[x[0].params.distance,
                 x[0].params.period,
                 x[0].analyzers.returns.get_analysis()['rtot'],
                 x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                 x[0].analyzers.sharpe.get_analysis()['sharperatio']] for x in back]

    par_df = pd.DataFrame(par_list, columns=['distance', 'period', 'return', 'dd', 'sharpe'])
    # qgrid.show_grid(par_df)


run_optimize('Pair')
