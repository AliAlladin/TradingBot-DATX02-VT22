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


def findPairs(stocks):
    print(stocks)
    start = '2017-02-08'
    end = '2020-02-08'
    window = 252
    data = pd.DataFrame()
    pairs = []

    tic = time.perf_counter()
    for stock in stocks:
        prices = yf.download(stock,start,end)
        data[stock] = prices['Close']
    toc = time.perf_counter()
    print('downloading data took ' , toc-tic , 'seconds')


    tic = time.perf_counter()
    for i in range(0,len(stocks)):
        for j in range(0, len(stocks)):
            if i > j:
                stock1data = data[stocks[i]]
                stock2data = data[stocks[j]]
                '''
                for k in range(len(stock2data)):
                    if pd.isna(stock2data[k]) or pd.isna(stock1data[k]):
                        print(stocks[i],stocks[j])
                        break;'''
                result = sm.OLS(stock2data, stock1data).fit()
                beta = result.params[0]
                p1 = adfuller((stock2data-beta*stock1data))[1]
                p2 = coint(stock1data, stock2data)[1]
                if p1 <0.05 and p2 < 0.05:
                    p = Pair(stocks[i],stocks[j],p1,p2)
                    pairs.append(p)
    toc = time.perf_counter()
    print('finding pairs took ' , toc - tic , ' seconds')
    return pairs


stocks_Airline = ['UAL','LUV','DAl','ALK','AAL']
stocks_advertising = ['IPG', 'OMC']
stocks_defence_aerospace = ['BA','GD', 'HWM', 'HII','LHX','LMT','NOC','RTX','TDY','TXT','TDG']
stocks_logistics = ['CHRW','EXPD','FDX','UPS']
stocks_apparel = ['NKE','PVH','RL', 'TPR', 'UAA', 'UA', 'VFC']
stocks_application_software = ['ADBE','ANSS','ADSK','CDNS','CTXS','INTU', 'NLOK', 'ORCL','PAYC','PTC','CRM','SNPS','TYL']#,'CDAY'
stocks_matrix = [stocks_Airline,stocks_advertising,stocks_defence_aerospace,stocks_logistics,stocks_apparel,stocks_application_software]
stocks_all = stocks_Airline+stocks_advertising+stocks_defence_aerospace+stocks_logistics+stocks_apparel +stocks_application_software
stocks_dj = ['AA','AAPL','AIG','AMGN','AXP','BA','BAC','C','CAT','CRM','CSCO','CVX','DD','DIS','GE','GM','GS','HD',
             'HON','HPQ','IBM','INTC','JNJ','JPM','KO','MCD','MDLZ','MMM','MO','MRK','MSFT','NKE','PFE','PG','RTX','T','TRV','UNH','V',
             'VZ','WBA','WMT','XOM']

def run(sample):
    myPairs = []
    myPairs=findPairs(sample)
    myPairsNew = []
    i=0
    for p in myPairs:
        myPairsNew.append(p)
        i += 1
        p.printP()
            #plt.plot(data[p.stock2]-p.beta*data[p.stock1])
            #plt.show()
    print('number of pairs ', i)
    my_pair_file = open('pairs.txt', 'w')

    for pair in myPairs:
        name1,name2=pair.getStockName()
        my_pair_file.write(name1+" "+name2+"\n")
    my_pair_file.close()


run(stocks_apparel)