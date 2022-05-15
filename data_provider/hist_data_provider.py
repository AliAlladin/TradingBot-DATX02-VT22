import pandas as pd
import yfinance as yf


def end_of_day(tickers: [str], days: int) -> pd.DataFrame:
    """
    Gives a DataFrame with end-of-day closing prices.
    :param tickers: List of tickers.
    :param days: Number of days.
    :return: A DataFrame with end-of-day data.
    """
    stocks = yf.download(tickers=tickers, period=(str(days) + "d"), interval="1d")['Adj Close']
    stocks = stocks.reset_index()
    return stocks
