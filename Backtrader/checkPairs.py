import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair2 import Pair2 as Pair
import time
from statsmodels.regression.rolling import RollingOLS


def checkPair(pairs):
    start = '2020-01-08'
    end = '2022-01-06'
    window = 252
    data = pd.DataFrame()
    size = len(pairs)
    newPairs = []
    stillCo = 0
    Plevels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
    futureP = {}
    for level in Plevels:
        futureP[level]=0

    for pair in pairs:
        prices = yf.download(pair.stock1,start,end)
        data[pair.stock1] = prices['Close']
        prices = yf.download(pair.stock2,start,end)
        data[pair.stock2] = prices['Close']
    for pair in pairs:
        stock1data = data[pair.stock1]
        stock2data = data[pair.stock2]
        #result = sm.OLS(stock2data, stock1data).fit()
        #beta = result.params[0]
        p1 = coint(stock1data, stock2data)[1]

        for level in Plevels:
            if p1 < level:
                futureP[level]= futureP[level]+1


        p = Pair(pair.stock1,pair.stock2,p1)
        newPairs.append(p)

        #plt.plot(stock2data-beta*stock1data)
        #plt.show()
    for level in Plevels:
        futureP[level]= futureP[level]/size
    my_pair_file = open('pairsAllCo.txt', 'w')
    #print(stillCo/(len(pairs)))
    for pair in newPairs:
        my_pair_file.write(pair.stock1+" "+pair.stock2+ " "+ pair.p1 + "\n")
    my_pair_file.close()
    print(futureP)
    return

    
def run():
    myPairs = []
    i=0
    my_pair_file = open('pairsDistinct.txt', 'r')
    for p in my_pair_file:
        stocks=p.split()
        stock1=stocks[0]
        stock2 = stocks[1]
        myPairs.append(Pair(stock1, stock2, 1.1))
    for p in myPairs:
        p.toString()
    checkPair(myPairs)


run()
