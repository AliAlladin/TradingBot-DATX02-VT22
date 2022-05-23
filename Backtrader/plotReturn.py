import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair2 import Pair2 as Pair
import pandas as pd
import matplotlib.ticker as mtick
def plotPair():

    start = '2022-04-14'  # yahoo gets the data for all dates before this date so use one day after the day you want to plot
    end = '2022-05-04'  # yahoo gets the data for all dates before this date so use one day after the day you want to plot
    plotsize=13 # size of plots
    prices = yf.download('^GSPC',start,end)
    SP = prices['Close'] #extracts closing prices
    index = SP.index  #extracts the index so we can make the results as a pandas.series
    ResultFile = open('resultToPlot.txt', 'r') #file where all results are
    values = []
    portfoliValueStart = 1000000 #the start value of the portfolio

    for line in ResultFile:
        values.append(float(line.split()[0])- portfoliValueStart) #converts the total portfolio value to money gained
    ValSer = pd.Series(values,index)
    data = pd.DataFrame()
    data['Pair trading'] = ValSer
    ax = data.plot()
    ax.tick_params(axis='both', which='major', labelsize=plotsize)
    ax.set_xlabel("Datum", fontsize=plotsize)
    ax.set_ylabel("Avkastning ($)", fontsize=plotsize)
    ax.legend(fontsize=plotsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.show()

def plotFib():
    start = '2022-04-22'  # yahoo gets the data for all dates before this date so use one day after the day you want to plot
    end = '2022-05-04'  # yahoo gets the data for all dates before this date so use one day after the day you want to plot
    invested = 1200000  #the Portfolio value at the start
    plotsize = 13

    prices = yf.download('^GSPC', start, end)
    SP = prices['Close'] #extracts closing prices
    startSP = SP.get(start)
    SP = (SP / startSP - 1) * 100 #convert to percentage return
    index = SP.index
    ResultFile = open('resultToPlot.txt', 'r') #file where all results are
    values = []

    for line in ResultFile:
        values.append(((float(line.split()[0]))/invested) *100) #convert to percentage return
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

