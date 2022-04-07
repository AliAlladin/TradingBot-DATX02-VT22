import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
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
    start_time = datetime.date(2010, 1, 1)
    significance = 0.65

    stocks = acquire_stocks()  # To acquire a list of stocks from our folder 'filtered_csv_data'

    pairs = find_pairs(stocks, start, end, significance)  # A list of pairs
    store_pairs(pairs, 'Pairs.txt')  # To write all the pairs in a .txt-file

    random.shuffle(pairs)  # To avoid affect the pairs by alphabetic order

    distinct_pairs = create_distinct_pairs(pairs)  # A list of pairs where a ticker only appears once
    store_pairs(distinct_pairs, 'Pairs1.txt')

    csv_pairs = sort_by_csv(start_time, distinct_pairs)  # A list of pairs sorted by availability in .csv-files
    store_pairs(csv_pairs, 'Pairs2.txt')


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
            # The name is on the form 'TICKER.A', we want 'TICKER-A' for Yahoo Finance
            y = x.split('.')
            x = y[0] + "-" + y[1]
        stocks.append(x)
    return stocks


# To find pairs in the interval [start, end] with a certain significance level
def find_pairs(stocks, start, end, significance):
    data = pd.DataFrame()
    pairs = []  # An initially empty list of pairs
    stocks_new = []  # A list of stocks with data available on the period

    # Downloading data
    tic = time.perf_counter()
    for i in range(0, len(stocks)):  # We go through all stocks, find the price from start to end.

        prices = yf.download(stocks[i], start, end)  # Daily data from Yahoo Finance
        # If the stock was listed in the time period, we check if it was listed in our period
        if not prices.empty:
            # To gather the first day and the last day of the available data from Yahoo Finance
            first_day = prices.index[1]
            first_day = str(first_day).split()[0]

            last_day = prices.index[-1]
            last_day += timedelta(days=1)
            last_day = str(last_day).split()[0]

            # To make sure that the stock has data at the end zones at our interval.
            if first_day == start and last_day == end:
                data[stocks[i]] = prices['Close']  # We store the closing price in data
                stocks_new.append(stocks[i])
    toc = time.perf_counter()
    print('Downloading data took ', toc - tic, 'seconds.')

    # Performing pair analysis
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
            if p1 < significance and p2 < significance:
                pairs.append(Pair(stocks[i], stocks[j]))
    toc = time.perf_counter()

    print('Finding pairs took ', toc - tic, ' seconds.')
    return pairs


# To store a list of pairs in textfile
def store_pairs(pairlist, textfile):
    # We open the file, write the pairs in the format "Ticker1 Ticker2" and then close it
    file = open(textfile, 'w')
    for pair in pairlist:
        stock1, stock2 = pair.get_pairs()
        file.write(stock1 + " " + stock2 + "\n")
    file.close()


# To find pairs with stocks that only appear once
def create_distinct_pairs(pairs):

    distinct_pairs = []
    used_stocks = []  # To keep track of which stocks we have put in our new list

    # For each pair of the old list of pairs, we try to add the pair if none of the two stocks are used.
    for pair in pairs:
        can_add = True  # Initially, we expect that we can add the pair to distinct pair.
        stocks = pair.get_pairs()  # get_pairs gives us (stock1, stock2)

        for stock in stocks:
            if stock in used_stocks:
                can_add = False  # The stock is already in a pair, we cannot add this par

        if can_add:
            # We can add the pair, we do so and say that both stocks are already used.
            distinct_pairs.append(pair)
            used_stocks.append(stocks[0])
            used_stocks.append(stocks[1])

    return distinct_pairs


# Returns the pairs as [priority, not priority] where priority is a sublist of stocks with the correct start date
def sort_by_csv(start, pairs):

    priority_list = []
    not_priority = []

    for pair in pairs:
        priority = True  # Initially, we assume that the date exists
        stocks = pair.get_pairs()
        for j in stocks:
            if "-" in j:  # The name is on the form 'TICKER-A' from Yahoo finance, we want 'TICKER.A' for csv
                y = j.split('-')
                j = y[0] + '.' + y[1]

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

    # We write the sorted list of pairs to a .txt-file
    total_list = priority_list + not_priority
    return total_list


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


main()
