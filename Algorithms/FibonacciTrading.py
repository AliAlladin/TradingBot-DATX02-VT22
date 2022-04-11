import datetime
import numpy as np
import pandas as pd
import pytz

pd.options.mode.chained_assignment = None  # default='warn'


class FibonacciStrategy:

    # Observer pattern stuff
    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, signal: dict):
        for obs in self._observers:
            obs.notify(self, signal)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def __init__(self, csv_data):
        """
        NOTE: csv_data must be a dataframe with columns = ['DateTime', t1, t2,...tn] where t1-tn are ticker symbols with
        only closing/current prices
        """
        self._observers = []  # List of observers to be notified

        # Parameters
        self.invested_amount = 10000  # The amount for which we invest
        self.period = 85  # Period of days to determine high or low swing

        # The Fibonacci ratios
        self.ratios = [0.382, 0.5, 0.618]

        start_index = extract_start_index(csv_data, self.period)
        self.data = csv_data[start_index:]  # Historic minute data for tickers
        self.data.reset_index(drop=True, inplace=True)
        self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])  # Change dtype of column DateTime to DateTime

        rows = self.data.columns[1:]
        emptyRows = [0] * len(rows)
        self.investments = pd.DataFrame({'Symbol': rows, 'Volume': emptyRows})
        self.investments.sort_values(by='Symbol', inplace=True)
        self.investments.reset_index(drop=True, inplace=True)

        # New dataframe with the fibonacci levels initiated with "False"
        self.invested_levels = pd.DataFrame(columns=self.data.columns[1:], index=self.ratios)
        for col in self.invested_levels.columns:
            self.invested_levels[col].values[:] = False

    def run(self, minute_data):
        """
        NOTE: minute_data must be a dataframe with columns = ['DateTime', t1, t2,...tn] where t1-tn are ticker
        symbols with closing prices only in order for the concat to be successful.
        """

        fibonacci_levels = []
        uptrend = False
        self.data.drop(0, inplace=True, axis=0)  # Remove the first row of the dataframe
        self.data.reset_index(inplace=True, drop=True)  # Resets index of dataframe
        self.data = updateFrame(self.data, minute_data)

        self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])  # Change dtype of column DateTime to DateTime


        for i in range(1, (len(self.data.columns))):  # Iterate through the tickers of the dataframe

            # Extracts ticker data for a specific ticker
            relevantData = self.data[['DateTime', self.data.columns[i]]].copy()
            ticker = relevantData.columns[1]

            relevantData[ticker] = pd.to_numeric(relevantData[ticker])  # Change dtype of column DateTime to DateTime

            price_now = relevantData.iloc[-1, 1]  # Latest recorded price of the current ticker
            max_point = relevantData.loc[relevantData[ticker].astype(np.float64).idxmax()]  # Date,value of the highest recorded price
            min_point = relevantData.loc[relevantData[ticker].astype(np.float64).idxmin()]  # Date,value of the lowest recorded price

            # Check dates fo if we are in an uptrend or downtrend
            if max_point[0] > min_point[0]:  # Note that the variables hold both a datetime type and int type
                uptrend = True  # We are in an uptrend
                # We calculate the Fibonacci support levels
                fibonacci_levels = [max_point[1] - (max_point[1] - min_point[1]) * ratio for ratio in self.ratios]

            elif min_point[0] > max_point[0]:
                uptrend = False  # We are in a downtrend

            # If we are in an uptrend, we want to buy the stocks at drawbacks (Fibonacci supports).
            if uptrend:
                for m in range(len(self.ratios) - 1):

                    ratio = self.ratios[m]

                    if price_now < fibonacci_levels[m] and not self.invested_levels.loc[ratio][ticker]:
                        # We have reached the level, so we buy some stocks
                        number_of_stocks = self.invested_amount / price_now
                        self.investments.loc[(self.investments.Symbol == ticker), 'Volume'] = number_of_stocks

                        self.notify_observers({"signal": "BUY", "symbol": ticker, "volume": number_of_stocks})

                        # We do not want to buy on consecutive days, so we say that we have invested at this level
                        self.invested_levels.loc[ratio][ticker] = True

                # We sell when the stock price is at a new high on the period
                if price_now == max_point[1]:
                    if True in self.invested_levels.values:

                        number_of_stocks = self.investments.loc[(self.investments.Symbol == ticker), 'Volume']
                        # Sell all stocks, close the position
                        self.notify_observers({"signal": "SELL", "symbol": ticker, "volume": number_of_stocks})

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            self.invested_levels.loc[self.ratios[n]][ticker] = False

            if not uptrend:
                if price_now == min_point[1]:
                    if True in self.invested_levels.values:
                        number_of_stocks = self.investments.loc[(self.investments.Symbol == ticker), 'Volume']
                        # Sell all stocks, close the position
                        self.notify_observers({"signal": "SELL", "symbol": ticker, "volume": number_of_stocks})

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            self.invested_levels.loc[self.ratios[n]][ticker] = False


# Method which extracts the starting index of the minute data
def extract_start_index(df, period: int):
    df['DateTime'] = pd.to_datetime(df['DateTime'])  # Change dtype of column DateTime to DateTime

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


def updateFrame(csv, minuteBars):
    dat = csv['DateTime']
    csvFrame = csv.reindex(sorted(csv.columns[1:]), axis=1)
    csvFrame.insert(0, 'DateTime', dat)

    minuteBars.sort_values(by='Symbol', inplace=True)
    emptyRow = [0] * len(csvFrame.columns)
    new_timezone = pytz.timezone("US/Eastern")
    csvFrame.loc[len(csv.index)] = emptyRow
    csvFrame.iloc[-1, 0] = datetime.datetime.now(new_timezone).strftime("%Y-%m-%d %H:%M:%S")

    for i in range(1, (len(csvFrame.columns))):
        csvFrame.iloc[-1, i] = minuteBars.iloc[i - 1]['Price']
    return csvFrame
