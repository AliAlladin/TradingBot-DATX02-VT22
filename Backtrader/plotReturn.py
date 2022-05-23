import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair2 import Pair2 as Pair
import pandas as pd
import matplotlib.ticker as mtick
def plotPair():

    start = '2022-04-14'  # en mer än datafilen
    end = '2022-05-04'  # en mer än datafilen
    invested = 120000
    plotsize=13
    prices = yf.download('^GSPC',start,end)
    SP = prices['Close']
    print(SP)
    index = SP.index
    print(index)
    ResultFile = open('resultToPlot.txt', 'r')
    values = []

    for line in ResultFile:
        values.append(float(line.split()[0])-1000000)
    ValSer = pd.Series(values,index)
    data = pd.DataFrame()
    #data['S&P'] = SP
    data['Pair trading'] = ValSer
    ax = data.plot()
    ax.tick_params(axis='both', which='major', labelsize=plotsize)
    ax.set_xlabel("Datum", fontsize=plotsize)
    ax.set_ylabel("Avkastning ($)", fontsize=plotsize)
    ax.legend(fontsize=plotsize)
    #ax.annotate('%0.0f' % round(values[-1]), xy=(0.97, values[-1]), xytext=(8, 0),
                     #xycoords=('axes fraction', 'data'), textcoords='offset points', ha='center')

    #ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.show()

def plotFib():
    start = '2022-04-22'  # en mer än datafilen
    startL = '2022-04-21'
    end = '2022-05-04'  # en mer än datafilen
    portfolio = 1000000 # bara för realtidshandel
    invested = 1200000
    plotsize = 13

    prices = yf.download('^GSPC', start, end)
    SP = prices['Close']
    print(SP)
    startSP = SP.get(startL)
    SP = (SP / startSP - 1) * 100
    index = SP.index
    print(index)
    ResultFile = open('resultToPlot.txt', 'r')
    values = []

    for line in ResultFile:
        values.append(((float(line.split()[0])-portfolio)/invested) *100) # -portfolio är bara för realtidshandeln då datan är i annat format
    ValSer = pd.Series(values, index)
    data = pd.DataFrame()
    data['Fibonacci retracements'] = ValSer
    data['S&P 500'] = SP
    ax = data.plot(xticks = index)
    ax.tick_params(axis='both', which='major', labelsize=plotsize)
    ax.set_xlabel("Datum", fontsize=plotsize)
    ax.set_ylabel("Avkastning (%)", fontsize=plotsize)
    ax.legend(fontsize=plotsize)
    ax.annotate('%0.02f%s' % (values[-1],'%'), xy=(1, values[-1]), xytext=(8, 0),
                xycoords=('axes fraction', 'data'), textcoords='offset points', ha='center')
    ax.annotate('%0.02f%s' % (SP.tolist()[-1], '%'), xy=(1, SP.tolist()[-1]), xytext=(8, 0),
                xycoords=('axes fraction', 'data'), textcoords='offset points', ha='center')


    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.show()
    print(index)


#plotPair()
plotFib()

