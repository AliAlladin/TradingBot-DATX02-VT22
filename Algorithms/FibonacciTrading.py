import csv
import datetime

import numpy as np
import pandas as pd
import pytz

pd.options.mode.chained_assignment = None  # default='warn'


class FibonacciStrategy:
    """
    Class that represents the fibonacci strategy.
    """

    def subscribe(self, observer) -> None:
        """
        Adds an observer to the list of observers.
        :param observer: Observer that should be attached to the observable.
        :return: None
        """
        self._observers.append(observer)

    def notify_observers(self, signal: dict) -> None:
        """
        Sends signal to all observers.
        :param signal: The signal that should be sent to observers.
        :return: None
        """
        for obs in self._observers:
            obs.notify(self, signal)

    def unsubscribe(self, observer) -> None:
        """
        Deletes an observer from the list of observers.
        :param observer: The observer that should be removed from observers.
        :return: None
        """
        self._observers.remove(observer)

    def __init__(self, path_to_csv: str):
        """
        Constructor for the class.
        :param path_to_csv: Path to the csv file where the histric data is saved.
        """

        self._observers = []  # List of observers to be notified
        self.csvPath = path_to_csv

        """
        NOTE: csv_data must be a dataframe with columns = ['DateTime', t1, t2,...tn] where t1-tn are ticker symbols with
        only closing/current prices
        """
        csv_data = pd.read_csv(path_to_csv)  # Convert the csv-file to a dataframe

        # Parameters
        self.invested_amount = 10000  # The amount for which we invest
        self.period = 10  # Period of days to determine high or low swing

        # The Fibonacci ratios
        self.ratios = [0.382, 0.5, 0.618]

        start_index = extract_start_index(csv_data, self.period)
        self.data = csv_data[start_index:]  # Historic minute data for tickers
        self.data.reset_index(drop=True, inplace=True)
        self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])  # Change dtype of column DateTime to DateTime

    """
    """

    def run(self, invested_levels: pd.DataFrame, minute_data: pd.DataFrame, investments: pd.DataFrame) -> None:
        """
        This function calculates whether there is a buy or sell opportunity given data.
        :param invested_levels: A DataFrame with information about which Fibonacci levels each share is invested in.
        :param minute_data: Latest stock prices. Must be a dataframe with columns = ['DateTime', t1, t2,...tn] where
                            t1-tn are ticker symbols with closing prices only in order for the concat to be successful.
        :param investments: DataDrame with the number of stocks bought in each share.
        :return: None
        """

        fibonacci_levels = []
        uptrend = False
        self.data.drop(0, inplace=True, axis=0)  # Remove the first row of the dataframe
        self.data.reset_index(inplace=True, drop=True)  # Resets index of dataframe
        self.data = update_data(self.csvPath, self.data, minute_data)

        self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])  # Change dtype of column DateTime to DateTime

        for i in range(1, (len(self.data.columns))):  # Iterate through the tickers of the dataframe

            # Extracts ticker data for a specific ticker
            relevant_data = self.data[['DateTime', self.data.columns[i]]].copy()
            ticker = relevant_data.columns[1]

            relevant_data[ticker] = pd.to_numeric(relevant_data[ticker])  # Change dtype of column DateTime to DateTime

            price_now = relevant_data.iloc[-1, 1]  # Latest recorded price of the current ticker
            max_point = relevant_data.loc[
                relevant_data[ticker].astype(np.float64).idxmax()]  # Date,value of the highest recorded price
            min_point = relevant_data.loc[
                relevant_data[ticker].astype(np.float64).idxmin()]  # Date,value of the lowest recorded price

            # Check dates fo if we are in an uptrend or downtrend
            if max_point[0] > min_point[0]:  # Note that the variables hold both a datetime type and int type
                uptrend = True  # We are in an uptrend
                # We calculate the Fibonacci support levels
                fibonacci_levels = [max_point[1] - (max_point[1] - min_point[1]) * ratio for ratio in self.ratios]

            elif min_point[0] > max_point[0]:
                uptrend = False  # We are in a downtrend

            # If we are in an uptrend, we want to buy the stocks at drawbacks (Fibonacci supports).
            if uptrend:
                for m in range(len(self.ratios)):

                    ratio = self.ratios[m]

                    if price_now < fibonacci_levels[m] and not invested_levels.loc[ratio][ticker]:
                        # We have reached the level, so we buy some stocks
                        number_of_stocks_before = investments.loc[(investments.symbol == ticker), 'volume'].tolist()[0]
                        number_of_stocks = self.invested_amount / price_now

                        investments.loc[
                            (investments.symbol == ticker), 'volume'] = number_of_stocks_before + number_of_stocks

                        self.notify_observers({"signal": "BUY", "symbol": ticker, "volume": number_of_stocks})

                        # We do not want to buy on consecutive days, so we say that we have invested at this level
                        invested_levels.loc[ratio][ticker] = True

                # We sell when the stock price is at a new high on the period
                if price_now == max_point[1]:
                    if True in invested_levels[ticker].values:

                        number_of_stocks = investments.loc[(investments.symbol == ticker), 'volume'].tolist()[0]
                        # Sell all stocks, close the position
                        self.notify_observers({"signal": "SELL", "symbol": ticker, "volume": number_of_stocks})

                        investments.loc[(investments.symbol == ticker), 'volume'] = 0

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            invested_levels.loc[self.ratios[n]][ticker] = False

            if not uptrend:
                if price_now == min_point[1]:
                    if True in invested_levels[ticker].values:
                        number_of_stocks = investments.loc[(investments.symbol == ticker), 'volume'].tolist()[0]
                        # Sell all stocks, close the position
                        self.notify_observers({"signal": "SELL", "symbol": ticker, "volume": number_of_stocks})

                        investments.loc[(investments.symbol == ticker), 'volume'] = 0

                        # We do no longer have a position in the ticker
                        for n in range(len(self.ratios)):
                            invested_levels.loc[self.ratios[n]][ticker] = False


def extract_start_index(df: pd.DataFrame, period: int) -> int:
    """
    Method that extracts the starting index of the minute data.
    :param df: The DataFrame from which the index should be extracted.
    :param period: Length of period.
    :return: Index of where the period starts in the DataFrame.
    """
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


def update_data(path: str, csv_df: pd.DataFrame, minute_bars: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the latest data to the DataFrame with historic data.
    :param path: Path to CSV-file.
    :param csv_df: CSV-file as DataFrame.
    :param minute_bars: DataFrame with latest stock prices.
    :return: Updated DataFrame with latest stock prices.
    """
    dat = csv_df['DateTime']
    csv_frame = csv_df.reindex(sorted(csv_df.columns[1:]), axis=1)
    csv_frame.insert(0, 'DateTime', dat)

    minute_bars.sort_values(by='Symbol', inplace=True)
    empty_row = [0] * len(csv_frame.columns)
    new_timezone = pytz.timezone("US/Eastern")
    csv_frame.loc[len(csv_df.index)] = empty_row
    csv_frame.iloc[-1, 0] = datetime.datetime.now(new_timezone).strftime("%Y-%m-%d %H:%M:%S")

    for i in range(1, (len(csv_frame.columns))):
        csv_frame.iloc[-1, i] = minute_bars.iloc[i - 1]['Price']

    # Converts last row of df to a list and sends it as a parameter to addToCSV()
    add_to_csv(path, csv_frame.iloc[-1].tolist())

    return csv_frame


def add_to_csv(path: str, row) -> None:
    """
    Adds a new row to the CSV-file
    :param path: Path to CSV-file.
    :param row: Row that should be added (as list).
    :return: None
    """
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
