import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair import Pair
import time
from statsmodels.regression.rolling import RollingOLS
import os
import sys  # To find out the script name (in argv[0])
from datetime import timedelta, date
import datetime

import math
import random


def main():
    start = '2019-03-22'
    end = '2022-03-22'
    #distinctStocks()
    # tryingOut(start,end)
    stocks=acquireList()
    pairs=findPairs(stocks,start,end)
    my_pair_file = open('Pairs.txt', 'w')
    for pair in pairs:
        stock1, stock2=pair.get_pairs()
        my_pair_file.write(stock1+" "+stock2+ "\n")
    my_pair_file.close()
    print(pairs)
    pairs=acquiringPair(pairs)
    print(pairs)
    my_pair_file = open('Pairs1.txt', 'w')
    for pair in pairs:
        stock1, stock2 = pair.get_pairs()
        my_pair_file.write(stock1 + " " + stock2 + "\n")
    my_pair_file.close()

def gettingDistinctDates():
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    datap = os.path.join(modpath, 'Data/filtered_csv_data/A.csv')
    my_pair_file = open(datap, 'r')
    distinctDates=[]
    for i in my_pair_file:
        j=i.split()[0]
        if j not in distinctDates:
            distinctDates.append(j)
    my_pair_file.close()
    my_pair_file = open('DistinctDates.txt', 'w')
    for i in distinctDates:
        my_pair_file.write(str(i)+ '\n')



def acquireList():
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
    return stocks


def tryingOut(start, end):
    stock = 'AIG'
    prices = yf.download(stock, start, end)
    print(prices)


def distinctStocks():
    my_pair_file = open('Backtrader/Pairs.txt', 'r')
    distinctStocks = []
    for i in my_pair_file:
        for j in i.split():
            if j not in distinctStocks:
                distinctStocks.append(j)
    print(len(distinctStocks))
    print(distinctStocks)


def acquiringPair(pairs):
    distinctStocks = []
    random.shuffle(pairs)
    newPairs = []
    for pair in pairs:
        add = True
        stocks = pair.get_pairs()
        for stock in stocks:
            if stock in distinctStocks:
                add = False
        if add == True:
            distinctStocks.append(stocks[0])
            distinctStocks.append(stocks[1])
            newPairs.append(pair)
    return newPairs

def findPairs(stocks, start, end):
    window = 252
    data = pd.DataFrame()
    pairs = []
    stocksNew = []
    tic = time.perf_counter()
    for i in range(0, len(stocks)):
        prices = yf.download(stocks[i], start, end)
        if not prices.empty:
            firstDayForStock = prices.index[1]
            firstDayForStock = str(firstDayForStock).split()[0]
            lastDayForStock = prices.index[-1]
            lastDayForStock += timedelta(days=1)
            lastDayForStock = str(lastDayForStock).split()[0]

            if str(firstDayForStock) == start and lastDayForStock == end:
                data[stocks[i]] = (prices['Close'])
                stocksNew.append(stocks[i])
    toc = time.perf_counter()
    # print('downloading data took ' , toc-tic , 'seconds')
    stocks = stocksNew
    print(len(stocks))
    tic = time.perf_counter()
    for i in range(0, len(stocks)):
        print(i)
        for j in range(i + 1, len(stocks)):
            stock1data = data[stocks[i]].tolist()
            stock2data = data[stocks[j]].tolist()
            stock1data = np.log10(stock1data)
            stock2data = np.log10(stock2data)
            result = sm.OLS(stock1data, sm.add_constant(stock2data)).fit()
            alpha = result.params[0]
            beta = result.params[1]
            p1 = adfuller(stock1data - beta * stock2data)[1]
            p2 = coint(stock1data, stock2data)[1]
            if p1 < 0.0002 and p2 < 0.0002:
                p = Pair(stocks[i], stocks[j])
                pairs.append(p)
    toc = time.perf_counter()
    plt.show()
    print('finding pairs took ', toc - tic, ' seconds')
    print(len(pairs))
    return pairs

def in_csv_file(start):

    my_pair_file = open('Pairs.txt', 'r')
    priority_list=[]
    not_priority=[]
    for i in my_pair_file:
        priority=True
        x=i.split()
        for j in x:
            modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
            datap = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(j)
            csv_file = open(datap, 'r')
            a=csv_file.readlines()[1]
            date=a.split()[0]
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if date>start:
                priority=False
            csv_file.close()

        if priority:
            priority_list.append(Pair(x[0], x[1]))
        else:
            not_priority.append(Pair(x[0], x[1]))
    priority_list = acquiringPair(priority_list)
    not_priority = acquiringPair(not_priority)
    my_pair_file.close()
    my_pair_file = open('Pairs2.txt', 'w')
    total_list=priority_list+not_priority
    for i in total_list:
        stock1 , stock2 = i.get_pairs()
        my_pair_file.write(stock1+ ' '+ stock2 +'\n')

start=datetime.date(2014, 6, 9)
in_csv_file(start)
