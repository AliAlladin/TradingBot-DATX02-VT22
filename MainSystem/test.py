import datetime
import os
import sys
import pandas as pd
import yfinance as yf
import datetime as dt


def end_of_day(tickers: [str], days: int):

    stock = yf.download(tickers=tickers, period=(str(days) + "d"), interval="1d")['Adj Close']

    return stock

print(end_of_day(['AAPL', 'TSLA', 'AMZN', 'NFLX'], 10))
