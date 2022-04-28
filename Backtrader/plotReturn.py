import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import yfinance as yf
from Pair2 import Pair2 as Pair
import pandas as pd
import matplotlib.ticker as mtick

start = '2011-01-14' #en mer än datafilen
end = '2013-01-08' #en mer än datafilen
invested = 120000

prices = yf.download('^GSPC',start,end)
SP = prices['Close']
startSP = SP.get(start)
SP =(SP/startSP-1 )*100
index = SP.index
print(index)
ResultFile = open('resultToPlot.txt', 'r')
values = []

for line in ResultFile:
    values.append(float(line.split()[0]))
ValSer = pd.Series(values,index)
data = pd.DataFrame()
#data['S&P'] = SP
data['Pair trading'] = ValSer
ax = data.plot()
ax.tick_params(axis='both', which='major', labelsize=15)
ax.set_xlabel("Datum", fontsize=15)
ax.set_ylabel("Avkastning", fontsize=15)
ax.legend(fontsize=15)

#ax.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.show()


