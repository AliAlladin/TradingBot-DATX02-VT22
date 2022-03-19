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
import math

def main():   
    start = '2017-02-07'
    end = '2020-02-08'
    stocks=acquireList()
    ## stocks=stocks[0:60]
    print(len(stocks))
    pairs=findPairs(stocks,start,end)
    my_pair_file = open('Data/Pairs.txt', 'w')
    for pair in pairs:
        stock1, stock2=pair.get_pairs()
        my_pair_file.write(stock1+" "+stock2+ "\n")
    my_pair_file.close()


def acquireList():
    stocks=[]
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    directory_in_str = os.path.join(modpath, 'Data/filtered_csv_data/')
    directory = os.fsencode(directory_in_str)
    for filename in os.listdir(directory):
        x=(str(filename))
        x=x.split('\'')[1]
        x=x.removesuffix('.csv')
        stocks.append(x)
    return stocks

def findPairs(stocks,start,end):
    print(stocks)
    window = 252
    data = pd.DataFrame()
    pairs = []
    stocksNew=[]
    tic = time.perf_counter()
    for i in range(0,len(stocks)):
        prices = yf.download(stocks[i],start,end)
        if not prices.empty:
            firstDayForStock=prices.index[1]
            firstDayForStock=str(firstDayForStock).split()[0]
            lastDayForStock=prices.index[-1]
            lastDayForStock += timedelta(days=1)
            lastDayForStock=str(lastDayForStock).split()[0]
            
            if str(firstDayForStock)==start and lastDayForStock==end:
                data[stocks[i]]=(prices['Close'])
                stocksNew.append(stocks[i])
    toc = time.perf_counter()
    # print('downloading data took ' , toc-tic , 'seconds')
    stocks=stocksNew
    tic = time.perf_counter()
    for i in range(0,len(stocks)):
        for j in range(i+1, len(stocks)):
            stock1data = data[stocks[i]].tolist()
            stock2data = data[stocks[j]].tolist()
            stock1data=np.log10(stock1data)
            stock2data=np.log10(stock2data)
            result = sm.OLS(stock1data,sm.add_constant(stock2data)).fit()
            alpha=result.params[0]
            beta = result.params[1]
            p1 = adfuller(stock1data-beta*stock2data)[1]
            p2 = coint(stock1data, stock2data)[1]
            if p1 <0.01 and p2<0.01:
                p = Pair(stocks[i],stocks[j])
                pairs.append(p)
                plt.scatter(stock1data,stock2data)
                max_x = stock2data.max()
                min_x = stock2data.min()
                x = np.linspace(min_x,max_x,1000)
                y = alpha+beta * x 
                plt.plot(y,x,'r')
    toc = time.perf_counter()
    plt.show()
    print('finding pairs took ' , toc - tic , ' seconds')
    print(len(pairs))
    return pairs
main()
