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
    start = '2019-02-08'
    end = '2022-02-08'
    window = 252
    data = pd.DataFrame()
    newPairs = []
    stillCo = 0

    for pair in pairs:
        prices = yf.download(pair.stock1,start,end)
        data[pair.stock1] = prices['Close']
        prices = yf.download(pair.stock2,start,end)
        data[pair.stock2] = prices['Close']
    for pair in pairs:
        stock1data = data[pair.stock1]
        stock2data = data[pair.stock2]
        result = sm.OLS(stock2data, stock1data).fit()
        beta = result.params[0]
        p1 = adfuller((stock2data-beta*stock1data))[1]
        p2 = coint(stock1data, stock2data)[1]

        if(p1 < 0.1 and p2 <0.1):
            stillCo += 1

        p = Pair(pair.stock1,pair.stock2,p1,p2)
        newPairs.append(p)

        plt.plot(stock2data-beta*stock1data)
        plt.show()

    my_pair_file = open('pairs2.txt', 'w')
    print(stillCo/(len(pairs)))
    for pair in newPairs:
        my_pair_file.write(pair.stock1+" "+pair.stock2+ " "+ pair.p1 +" "+pair.p2+ "\n")
    my_pair_file.close()
    return

    
def run():
    myPairs = []
    i=0
    my_pair_file = open('pairs2.txt', 'r')
    for p in my_pair_file:
        stocks=p.split()
        stock1=stocks[0]
        stock2=stocks[1]
        myPairs.append(Pair(stock1,stock2,1.1,1.1))
    for p in myPairs:
        p.toString()
    checkPair(myPairs)
run()








