import yfinance as yf


def end_of_day(tickers: [str], days: int):
    stocks = yf.download(tickers=tickers, period=(str(days) + "d"), interval="1d")['Adj Close']
    stocks = stocks.reset_index()
    return stocks
