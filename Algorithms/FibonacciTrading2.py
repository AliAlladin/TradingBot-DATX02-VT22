import os
from datetime import time

import pandas as pd
import sys
import yfinance as yf

'''
Assuming that the input data consists of 1 dataframe w/ the columns: "Date" and each ticker's name w/ 
respective closing prices for each date
'''

# This data is to be provided by the database.
data = yf.download(tickers="AAPL A AA AMZN", period="7d", interval="1m")['Close']
data.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testdata.csv'), index=True)
testData = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testdata.csv'))


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
    def __init__(self, ticker_data):
        self._observers = []  # List of observers to be notified

        # Parameters
        self.invested_amount = 10000  # The amount for which we invest
        self.period = 3  # Period of days to determine high or low swing

        # The Fibonacci ratios
        self.ratios = [0.382, 0.5, 0.618]

        self.data = ticker_data
        self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])  # Convert column to datetime type

        self.oldDate = self.data.iloc[-1]['Datetime'].date()  # Fetch the most recent date

        # New dataframe with the fibonacci levels initiated with "False"
        self.invested_levels = pd.DataFrame(columns=self.data.columns[1:], index=self.ratios)
        for col in self.invested_levels.columns:
            self.invested_levels[col].values[:] = False

    def run(self):
        fibonacci_levels = []
        uptrend = False

        # Collects all indices for when market opens
        indices = []
        for i in range(len(self.data)):
            if self.data.iloc[i]['Datetime'].time() == time(9, 30, 00):
                indices.append(i)

        start_index = indices[len(indices) - self.period]

        for i in range(1, (len(self.data.columns))):

            # Extracts ticker data for a specific period into a dataframe
            relevantData = self.data[['Datetime', self.data.columns[i]]][start_index:].copy()
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

                        self.notify_observers({
                            "signal": "BUY",
                            "symbol": ticker,
                            "volume": number_of_stocks
                        })

                        # We do not want to buy on consecutive days, so we say that we have invested at this level
                        self.invested_levels.loc[ratio][ticker] = True

                # We sell when the stock price is at a new high on the period
                if price_now == date_high[1]:
                    if True in self.invested_levels.values:
                        # Sell all stocks, close the position
                        self.notify_observers({
                            "signal": "SELL",
                            "symbol": ticker,
                        })

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            self.invested_levels.loc[self.ratios[n]][ticker] = False

            if not uptrend:
                if price_now == date_low[1]:
                    if True in self.invested_levels.values:
                        # Sell all stocks, close the position
                        self.notify_observers({
                            "signal": "SELL",
                            "symbol": ticker,
                        })

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            self.invested_levels.loc[self.ratios[n]][ticker] = False


# ----------------------------------------------------------------------------------------------------------------------
k = FibonacciStrategy(testData)
k.run()
