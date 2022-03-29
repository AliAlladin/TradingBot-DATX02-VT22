import datetime
import os
import sys
import pandas as pd
import yfinance as yf
import datetime as dt


def end_of_day(tickers: [str], days: int):
    start = dt.date.today() - dt.timedelta(days=days)
    end = dt.date.today()
    data = yf.download('AAPL', start=start, end=end)['Adj Close']
    for ticker in tickers:
        stock = yf.download(ticker, start=start, end=end)['Adj Close']
        data = pd.concat([data, stock], axis=1)

    del data['Adj Close']
    return data


print(end_of_day(['AAPL, TSLA, AMZN, NFLX'], 30))