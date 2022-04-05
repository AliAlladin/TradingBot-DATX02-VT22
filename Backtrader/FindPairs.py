import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair import Pair
import time
import os
import sys  # To find out the script name (in argv[0])
from datetime import timedelta
import random
import datetime


# To find pairs in a specific interval
def main():
    # Date of start and end. Observe that it must be a day when the market is open.
    start = '2011-01-07'
    end = '2014-01-07'

    stocks = acquire_stocks() # To acquire a list of stocks from our folder 'filtered_csv_data'

    # Returns a list of distinct_stocks
    # get_distinct_stocks()

    pairs = find_pairs(stocks, start, end) # To find pairs from a list of stocks in the period [start, end]

    # To write all the pairs in a .txt-file
    store_pairs(pairs, 'Pairs.txt')

    distinct_pairs = create_distinct_pairs(pairs) # To get a list of pairs where a ticker only appears once

    # We save these pairs in another .txt-file
    store_pairs(distinct_pairs, 'Pairs1.txt')


# To get a list of stocks from our folder 'filtered_csv_data'
def acquire_stocks():
    # To create the directory for which we read the ticker names.
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    directory_in_str = os.path.join(modpath, 'Data/filtered_csv_data/')
    directory = os.fsencode(directory_in_str)

    # For each .csv-file, we read the stock name and append it do a list.
    stocks = []
    for filename in os.listdir(directory):
        x = (str(filename))
        x = x.split('\'')[1]
        x = x.removesuffix('.csv')

        # If both an A-share and a B-share of a stock exists, we include both
        if "." in x:
            # The name is on the form 'TICKER.A', we want 'TICKER-A'
            y = x.split('.')
            x = y[0] + "-" + y[1]
        stocks.append(x)
    return stocks


# To find pairs in the interval [start, end]
def find_pairs(stocks, start, end):
    data = pd.DataFrame()

    pairs = []  # An initially empty list of pairs
    stocks_new = []  # A list of stocks with data available on the period

    tic = time.perf_counter()
    # We go through all stocks, find the price from start to end.
    for i in range(0, len(stocks)):
        # Daily data from Yahoo Finance
        prices = yf.download(stocks[i], start, end)

        # If the stock was listed in the time period, we check if it was listed in our period
        if not prices.empty:
            # To gather the first day and the last day of the available data from Yahoo Finance
            first_day = prices.index[1]
            first_day = str(first_day).split()[0]

            last_day = prices.index[-1]
            last_day += timedelta(days=1)
            last_day = str(last_day).split()[0]

            # To make sure that the stock has data at the end zones at our interval.
            if str(first_day) == start and last_day == end:
                data[stocks[i]] = (prices['Close'])  # We store the closing price in data
                stocks_new.append(stocks[i])
    toc = time.perf_counter()
    print('Downloading data took ', toc - tic, 'seconds.')

    stocks = stocks_new

    tic = time.perf_counter()
    # We try to find pairs for all available stocks
    for i in range(0, len(stocks)):
        for j in range(i + 1, len(stocks)):
            # To receive data for both stocks
            stock1data = np.log10(data[stocks[i]].tolist())
            stock2data = np.log10(data[stocks[j]].tolist())

            # An ordinary linear regression
            result = sm.OLS(stock1data, sm.add_constant(stock2data)).fit()
            beta = result.params[1]

            # We make use of the Augmented Dickey-Fuller test to check for co-integration.
            p1 = adfuller(stock1data - beta * stock2data)[1]
            p2 = coint(stock1data, stock2data)[1]

            # If the p-values are lower than the significance level, they are a pair
            sig = 0.65
            if p1 < sig and p2 < sig:
                p = Pair(stocks[i], stocks[j])
                pairs.append(p)
    toc = time.perf_counter()

    plt.show()
    print('finding pairs took ', toc - tic, ' seconds')
    return pairs


# To store a list of pairs in textfile
def store_pairs(pairlist, textfile):
    # We open the file, write the pairs in the format "Ticker1 Ticker2" and then close it
    file = open(textfile, 'w')
    for pair in pairlist:
        stock1, stock2 = pair.get_pairs()
        file.write(stock1 + " " + stock2 + "\n")
    file.close()


def create_distinct_pairs(pairs):
    # To avoid affect the pairs by alphabetic order, we shuffle the list of pairs
    random.shuffle(pairs)

    distinct_pairs = []
    used_stocks = []  # To keep track of which stocks we have put in our new list

    # For each pair of the old list of pairs, we try to add the pair if none of the two stocks are used.
    for pair in pairs:
        can_add = True  # Can we add the pair to the new list? Initially, we expect that we can.
        stocks = pair.get_pairs()  # get_pairs gives us (stock1, stock2) # TODO: Bad name for a function?

        for stock in stocks:
            if stock in used_stocks:
                can_add = False  # The stock is already in a pair, we cannot add this par

        if can_add:
            # We can add the pair, we do so and say that both stocks are already used.
            distinct_pairs.append(pair)
            used_stocks.append(stocks[0])
            used_stocks.append(stocks[1])

    return distinct_pairs


# To create a .txt-file of distinct dates
def get_distinct_dates():
    # We open a data-file and put all dates in a .txt-file
    data_file = open('Data/filtered_csv_data/A.csv', 'r')
    distinct_dates = []  # A list to keep track of the dates

    # Looping through the data file and append our distinct dates
    for row in data_file:
        date = row[0]
        if date not in distinct_dates:
            distinct_dates.append(date)
    data_file.close()

    # We write the distinct dates in a .txt-file
    date_file = open('DistinctDates.txt', 'w')
    for i in distinct_dates:
        date_file.write(str(i) + "\n")


# To create a list of distinct stocks in a .txt-file of pairs.
def get_distinct_stocks():
    # We open the .txt-file of pairs
    my_pair_file = open('Backtrader/Pairs.txt', 'r')
    distinct_stocks = []

    # We go through all stocks in all pairs to see if they have been used before
    for row in my_pair_file:
        for stock in row.split():
            if stock not in distinct_stocks:
                distinct_stocks.append(stock)

    return distinct_stocks


# To check if the files contain the correct starting time.
# The function will store the pairs as [priority, not priority] where priority is a list of stocks with the
# correct start date
def in_csv_file(start):

    my_pair_file = open('Backtrader/Pairs.txt', 'r')
    priority_list = []
    not_priority = []

    for pair in my_pair_file:
        priority = True  # We assume that the date exists
        stocks = pair.split()
        for j in stocks:
            # The path to find the stock
            modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
            datap = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(j)

            # We open the stocks file and read the second line, which contains the first date.
            csv_file = open(datap, 'r')
            line = csv_file.readlines()[1]
            date = line.split()[0]
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

            # If the start of the .csv-file is later than our starting point for a stock, the pair is not prioritized
            if date > start:
                priority = False
            csv_file.close()

        if priority:
            priority_list.append(Pair(stocks[0], stocks[1]))
        else:
            not_priority.append(Pair(stocks[0], stocks[1]))

    my_pair_file.close()

    # We write the sorted list of pairs to a .txt-file
    total_list = priority_list + not_priority
    store_pairs(total_list, 'Pairs2.txt')


start_time = datetime.date(2010, 1, 1)
in_csv_file(start_time)
