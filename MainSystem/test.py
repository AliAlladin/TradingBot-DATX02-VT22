import datetime
import os
import sys
import pandas as pd
import yfinance as yf
import datetime as dt


def end_of_day(tickers: [str], days: int):
    data = yf.download(tickers='AAPL', period=(str(days) + "d"), interval="1d")['Adj Close']
    for ticker in tickers:
        stock = yf.download(tickers=ticker, period=(str(days) + "d"), interval="1d")['Adj Close']
        data = pd.concat([data, stock], axis=1)

    del data['Adj Close']

    return data

print(end_of_day(['AAPL, TSLA, AMZN, NFLX'], 10))