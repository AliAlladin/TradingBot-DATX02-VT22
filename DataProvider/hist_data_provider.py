import yfinance as yf

'''
Returns a DataFrame with end-of-day closing prices given list of tickers and number of days.
'''
def end_of_day(tickers: [str], days: int):
    stocks = yf.download(tickers=tickers, period=(str(days) + "d"), interval="1d")['Adj Close']
    stocks = stocks.reset_index()
    return stocks
