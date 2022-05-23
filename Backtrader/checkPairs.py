import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair2 import Pair2 as Pair
from scipy.stats import t
import time
from statsmodels.regression.rolling import RollingOLS


def checkPair(pairs):
    start = '2008-01-08'
    end = '2009-01-08'
    data = pd.DataFrame()
    size = len(pairs)
    newPairs = []
    stillCo = 0
    Plevels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
    futureP = {}
    pValues = []
    for level in Plevels:
        futureP[level] = 0

    for pair in pairs:
        if not pair.stock1 in data.columns:
            prices = yf.download(pair.stock1, start, end)
            data[pair.stock1] = prices['Close']
        if not pair.stock2 in data.columns:
            prices = yf.download(pair.stock2, start, end)
            data[pair.stock2] = prices['Close']
    for pair in pairs:
        stock1data = data[pair.stock1]
        stock2data = data[pair.stock2]
        p1 = coint(stock1data, stock2data)[1]
        pValues.append(p1)
        results = loadResults()

        for level in Plevels:
            if p1 < level:
                futureP[level] = futureP[level] + 1

        p = Pair(pair.stock1, pair.stock2, p1)
        newPairs.append(p)

    for level in Plevels:
        futureP[level] = futureP[level] / size
    my_pair_file = open('pairsAllCo.txt', 'w')

    for pair in newPairs:
        my_pair_file.write(pair.stock1 + " " + pair.stock2 + " " + pair.p1 + "\n")
    my_pair_file.close()
    plotResults(pValues, results)
    mean = np.mean(pValues)
    print('mean: ', mean)
    print(futureP)
    return


def run():
    myPairs = []
    i = 0
    my_pair_file = open('pairsAll.txt', 'r')
    for p in my_pair_file:
        stocks = p.split()
        stock1 = stocks[0]
        stock2 = stocks[1]
        myPairs.append(Pair(stock1, stock2, 1.1))
    for p in myPairs:
        p.toString()
    checkPair(myPairs)


def loadResults():
    file = open('resPair.txt', 'r')
    res = []
    for line in file:
        res.append(float(line.rstrip()) - 100000)
    return res


def plotResults(pValues, results):
    plotsize = 13
    plt.scatter(pValues, results)
    linex = np.linspace(0, 1, 100)
    liney = np.linspace(0, 0, 100)
    plt.plot(linex, liney, 'black', linestyle='dashed')
    plt.xlabel('p-värde', fontsize=plotsize)
    plt.ylabel('Avkastning ($)', fontsize=plotsize)
    plt.xticks(size=plotsize)
    plt.yticks(size=plotsize)
    plt.show()


def plotAll():
    plotsize = 13
    file_res = open('resPairAll.txt', 'r')
    file_p = open('AllPVal.txt', 'r')
    res = []
    p = []
    for line in file_res:
        res.append(float(line) - 100000)
    for line in file_p:
        p.append(float(line))
    plt.scatter(p, res)
    linex = np.linspace(0, 1, 100)
    liney = np.linspace(0, 0, 100)
    plt.plot(linex, liney, 'black', linestyle='dashed')
    plt.xlabel('p-värde', fontsize=plotsize)
    plt.ylabel('Avkastning ($)', fontsize=plotsize)
    plt.xticks(size=plotsize)
    plt.yticks(size=plotsize)
    reg = sm.OLS(res, sm.add_constant(p)).fit()
    print(reg.summary())
    beta = reg.params[1]
    alpha = reg.params[0]
    y = alpha + linex * beta
    plt.plot(linex, y, 'g')
    plt.show()


# plotAll()
run()

