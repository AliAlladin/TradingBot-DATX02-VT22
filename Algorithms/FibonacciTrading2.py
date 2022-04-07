import os
import sys
from datetime import time, date
import yfinance as yf
import pandas as pd

'''
Assuming that the input data consists of 1 dataframe w/ the columns: "Date" and each ticker's name w/ 
respective closing prices for each date
'''

# This data is to be provided by the database.
testCSV = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testData.csv'))
minute = yf.download(tickers="A AA AAP AMZN", period="3d", interval="1m")['Close']
minute.reset_index(inplace=True)
minute.rename(columns={'Datetime': 'DateTime'}, inplace=True)


class FibonacciStrategy:

    # Observer pattern stuff
    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, signal: dict):
        for obs in self._observers:
            obs.notify(self, signal)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    # Initialization of class
    def __init__(self, csv_data):
        self._observers = []  # List of observers to be notified

        # Parameters
        self.invested_amount = 10000  # The amount for which we invest
        self.period = 85  # Period of days to determine high or low swing

        # The Fibonacci ratios
        self.ratios = [0.382, 0.5, 0.618]

        start_index = extract_start_index(csv_data, self.period)
        self.data = csv_data[start_index:]  # Historic minute data for tickers
        self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])

        # New dataframe with the fibonacci levels initiated with "False"
        self.invested_levels = pd.DataFrame(columns=self.data.columns[1:], index=self.ratios)
        for col in self.invested_levels.columns:
            self.invested_levels[col].values[:] = False

    def run(self, minute_data):
        fibonacci_levels = []
        uptrend = False

        self.data = pd.concat([self.data, minute_data], axis=0)
        self.data.drop(0, inplace=True, axis=0)
        self.data.reset_index(inplace=True, drop=True)

        for i in range(1, (len(self.data.columns))):

            # Extracts ticker data for a specific period into a dataframe
            relevantData = self.data[['DateTime', self.data.columns[i]]].copy()
            ticker = relevantData.columns[1]
            print(relevantData)

            price_now = relevantData.iloc[-1, 1]  # Latest data point/closing price
            date_high = relevantData.loc[relevantData[ticker].idxmax()]  # Date and value of the highest closing price
            date_low = relevantData.loc[relevantData[ticker].idxmin()]  # Date and value of the lowest closing price

            # Are we in an uptrend or a downtrend?
            if date_high[0] > date_low[0]:
                uptrend = True  # We are in an uptrend
                # We calculate the Fibonacci support levels
                fibonacci_levels = [date_high[1] - (date_high[1] - date_low[1]) * ratio for ratio in self.ratios]

            elif date_low[0] > date_high[0]:
                uptrend = False  # We are in a downtrend

            # If we are in an uptrend, we want to buy the stocks at drawbacks (Fibonacci supports).
            if uptrend:
                for m in range(len(self.ratios) - 1):

                    ratio = self.ratios[m]

                    if price_now < fibonacci_levels[m] and not self.invested_levels.loc[ratio][ticker]:
                        # We have reached the level, so we buy some stocks
                        number_of_stocks = self.invested_amount / price_now

                        self.notify_observers({"signal": "BUY", "symbol": ticker, "volume": number_of_stocks})

                        # We do not want to buy on consecutive days, so we say that we have invested at this level
                        self.invested_levels.loc[ratio][ticker] = True

                # We sell when the stock price is at a new high on the period
                if price_now == date_high[1]:
                    if True in self.invested_levels.values:
                        # Sell all stocks, close the position
                        self.notify_observers({"signal": "SELL", "symbol": ticker, })

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            self.invested_levels.loc[self.ratios[n]][ticker] = False

            if not uptrend:
                if price_now == date_low[1]:
                    if True in self.invested_levels.values:
                        # Sell all stocks, close the position
                        self.notify_observers({"signal": "SELL", "symbol": ticker, })

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            self.invested_levels.loc[self.ratios[n]][ticker] = False


# Method which extracts the starting index of the minute data
def extract_start_index(df, period: int):
    start_index = 0
    count = 0
    for i in range(len(df.index) - 1, 0, -1):
        if count == period:
            break
        index_date = df.iloc[i]['DateTime'].date()
        if df.iloc[i - 1]['DateTime'].date() != index_date:
            count += 1
            start_index = i
    return start_index


# ----------------------------------------------------------------------------------------------------------------------
k = FibonacciStrategy(testCSV)
k.run(minute)
