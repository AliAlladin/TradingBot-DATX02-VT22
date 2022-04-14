import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

stock = 'AMZN'
start = '2018-01-07'
half = '2018-04-07'
end = '2018-06-07'
colors = ['black', 'r', 'r', 'r', 'black']
ratios = [0.618, 0.5, 0.382]
lines = ['--', '-.', '-']

half_data = yf.download(stock, start, half)['Close']
high = max(half_data)
low = min(half_data)
levels = [low + (high - low) * ratio for ratio in ratios]
print(levels)

full_data = yf.download('AMZN', start, end)['Close']
plt.plot(full_data)
plt.ylabel('Pris ($)')
plt.xlabel('Datum')

half_days = len(half_data.index[:])
days = len(full_data.index[:])

plt.plot(pd.Series([high]*half_days, half_data.index[:]), ls='--', label='100%', color=colors[0])
for i in range(len(levels)):
    pd_series = pd.Series([levels[i]]*days, full_data.index[:])
    plt.plot(pd_series, color=colors[i+1], label=str(ratios[i]*100)+'%', ls=lines[i])

plt.plot(pd.Series([low]*half_days, half_data.index[:]), ls='--', label='0%', color=colors[4])
plt.legend(loc="upper left")
plt.show()
