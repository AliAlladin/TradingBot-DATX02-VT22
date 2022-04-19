import datetime
import os  # To get the searchpath
import sys  # To find out the script name (in argv[0])

'''import pandas as pd Do we need this?
pd.options.mode.chained_assignment = None'''
from Pair import *
from samuelStrategy import *  # Import our Strategies

# Global variables
modpath = os.path.dirname(os.path.dirname(sys.argv[0]))  # Individual os paths
todate = datetime.date(2019, 5, 1)  # Last date to trade
invested = 1000  # How much to invest in each stock
start_date = datetime.datetime(2017, 1, 1, 9, 30, 00)  # Start  date
end_date = datetime.datetime(2019, 1, 1, 16, 00, 00)  # Ending datev
datap = os.path.join(modpath, 'Results/result.csv')  # The data of pairs comes from Pairs.txt which we read
my_result_file = open(datap, 'w')  # Saving all our trades in a file


# Main function starts either strategy
def main():
    # StrategyOne()
    StrategyTwo()


# Pair Trading
def StrategyOne():
    cerebro = bt.Cerebro()  # Instantiate Cerebro engine. This is the main control center / brain
    datap = os.path.join(modpath, 'Backtrader/Pairs.txt')  # The data of pairs comes from Pairs.txt which we read
    my_pair_file = open(datap, 'r')  # Where all the pairs are saved
    endValueForEachPair = []  # List containing the portfolio value for each pair traded

    # We run backtrader for each pair
    for line in my_pair_file:
        pairs = []  # A list of Pairs (see Pair.py)
        stocks = line.split()
        stock1 = stocks[0]
        stock2 = stocks[1]
        cerebro = bt.Cerebro()  # Create the backtrader object
        pairs.append(Pair(stock1, stock2))
        for ticker in stocks:  # Adds data for the two stock in that pair
            add_data(cerebro, ticker)  # Add data to backtrader
        my_result_file.write(
            "Pair: " + stock1 + " " + stock2 + "\n")  # In the file to know whcih trades below belong to this pair
        cerebro.addstrategy(Strategy_pairGen, distance=3, period=100, invested=invested,
                            todate=todate,
                            my_result_file=my_result_file)  # Add our strategy with right values on the parameters
        endValueForEachPair.append(run(cerebro))  # Run the program and save the portfolio value in the end
    total_portfolio_value = sum(endValueForEachPair) - len(
        endValueForEachPair) * invested  # Calculate the profit for the total portfolio (all pairs)
    print(total_portfolio_value)
    my_result_file.close()


# Fibonacci
def StrategyTwo():
    endValueForEachStock = []
    my_stock_file = open('Stocks.txt', 'r')
    # Only difference here is that here we only have one stock
    for stock in my_stock_file:
        cerebro = bt.Cerebro()
        stock_name = stock.split()[0]
        add_data(cerebro, stock_name)
        my_result_file.write("Stock: " + stock_name + "\n ")
        cerebro.addstrategy(Strategy_fibonacci, stock_name=stock_name, invested=1000, period=50,
                            todate=todate, my_result_file=my_result_file)
        endValueForEachStock.append(run(cerebro))
    total_portfolio_value = sum(endValueForEachStock) - len(endValueForEachStock) * 100000
    my_result_file.close()


# Function to add data to backtrader
def add_data(cerebro, stock):
    CSV_file_path = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(stock)  # Full path to csv-file
    data = bt.feeds.GenericCSVData(
        dataname=CSV_file_path,  # Full path to csv-file
        fromdate=start_date,
        todate=end_date,

        nullvalue=0.0,  # Used for replacing NaN-values with 0

        dtformat='%Y-%m-%d %H:%M:%S',  # Used to parse the datetime CSV field. Default %Y-%m-%d
        tmformat='%H:%M:%S',  # Used to parse the time CSV field if present

        datetime=0,  # Column containing the date
        time=-1,  # Column containing the time field if separate from the datetime field. -1 if not present.

        # For each below, reference the corresponding index from the data

        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,

        openinterest=-1,  # -1 if no such column exists
        timeframe=bt.TimeFrame.Minutes,
    )
    cerebro.adddata(data)


# Setting up the environment in backtrader and running the simulation
def run(cerebro):
    cerebro.broker.setcash(100000.0)  # Irrelevant, just so high that we does not go below 0
    cerebro.broker.setcommission(commission=0)  # Set the commission - 0.1% ... divide by 100 to remove the %
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())  # Print starting portfolio value
    cerebro.run()  # Core method to perform backtesting
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())  # Print final portfolio value

    try:  # If we want to plot each simulation of each pair
        cerebro.plot()  # To plot the trades
    except IndexError:
        print('prob length 0')
    return cerebro.broker.getvalue()


main()
