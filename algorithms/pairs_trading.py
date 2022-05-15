import numpy as np
import pandas as pd
import statsmodels.api as sm

pd.options.mode.chained_assignment = None  # default='warn'


class PairsTrading:
    """
    This class receives a dataframe containing the latest prices for each ticker.
    It will go through each ticker, find its pair and perform the strategy on that pair in order
    to check whether or not we should sell or buy a either of the stocks of that pair. In that case,
    a sell/buy sigal will be passed back to Main.
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

    def update_pairs(self, info: dict) -> None:
        """
        Sends information to be updated to observers.
        :param info: The new information.
        :return: None
        """
        for obs in self._observers:
            obs.update_info(self, info)

    def unsubscribe(self, observer):
        """
        Deletes an observer from the list of observers.
        :param observer: The observer that should be removed from observers.
        :return: None
        """
        self._observers.remove(observer)

    def __init__(self, distance: int, period: int, invested_amount: int):
        """
        Constructor for the class.
        :param distance: -
        :param period: -
        :param invested_amount: Amount to be invested in each trade.
        """

        self._observers = []  # List of observers to be notified

        # The parameters that are to be varied to optimize the model
        self.distance = distance
        self.period = period
        self.invested_amount = invested_amount

    def run(self, pairs: pd.DataFrame, latest_prices: pd.DataFrame, hist_prices: pd.DataFrame) -> None:
        """
        This function calculates whether there is a buy or sell opportunity given data.
        :param pairs: DataFrame with the pairs of stocks.
        :param latest_prices: DataFrame with the latest price of each stock.
        :param hist_prices: DataFrame with end-of-day for each stock.
        :return: None
        """
        for i in range(len(pairs.index)):

            # Fetches a pair and the latest prices for each of the tickers
            t1 = pairs['t1'][i]  # Ticker symbol
            t2 = pairs['t2'][i]  # Ticker symbol

            # Latest minute data for ticker. Only 1 data point.
            tick1 = latest_prices.loc[latest_prices['Symbol'] == t1]
            tick2 = latest_prices.loc[latest_prices['Symbol'] == t2]

            '''
            Creates a new dataframe with only the historical closing prices for the specific pair.
            By default, the alpaca API will return today's candle even though it is not closed. This is incomplete.
            We update the last row later.
            '''
            data_df = pd.concat([hist_prices[t1], hist_prices[t2]], axis=1, join='inner', keys=[t1, t2], )

            # Update the last row with the minute data
            try:
                data_df.iloc[-1] = [tick1.iat[0, 1], tick2.iat[0, 1]]
            except Exception as e:
                print(e)
                continue
            data_df = data_df.astype(np.float64)

            # Perform a linear regression to calculate the spread
            result = sm.OLS(data_df[t1], data_df[t2]).fit()
            beta = result.params[0]
            spread = []

            for k in range(0, len(data_df)):
                spread.append(data_df[t1][k] - beta * data_df[t2][k])

            # Calculation of the Z-score
            mean = np.mean(spread)
            std = np.std(spread)
            z_score = (spread[len(data_df) - 1] - mean) / std

            # To know how much we need to buy of each stock
            shares_stock1 = self.invested_amount / data_df[t1][len(data_df) - 1]
            current_ratio = data_df[t1][len(data_df) - 1] / data_df[t2][len(data_df) - 1]

            # If we don't have a position in this pair
            if not pairs['active'][i]:
                # We check whether the Z-score is unusually high or low (>distance or <-distance)
                if z_score > self.distance:
                    # High Z-score, we sell stock 1 and buy stock 2

                    # Send sell signal to main
                    shares_stock1 = round(shares_stock1)
                    self.notify_observers({"signal": "SELL", "symbol": pairs['t1'][i], "volume": shares_stock1})

                    shares_stock2 = shares_stock1 * current_ratio

                    # Send buy signal to main
                    self.notify_observers({"signal": "BUY", "symbol": pairs['t2'][i], "volume": shares_stock2})

                    # Description of our position
                    self.update_pairs({'t1': pairs['t1'][i],
                                       't2': pairs['t2'][i],
                                       'long': False,
                                       'shares_stock1': shares_stock1,
                                       'shares_stock2': shares_stock2,
                                       'active': True})

                # The Z-score is unusually low, we buy stock1 and sell stock2
                elif z_score < -self.distance:

                    shares_stock2 = round(shares_stock1 * current_ratio)

                    # Send sell signal to main
                    self.notify_observers({"signal": "SELL", "symbol": pairs['t2'][i], "volume": shares_stock2})

                    shares_stock1 = (shares_stock2 / current_ratio)

                    # Send buy signal to main
                    self.notify_observers({"signal": "BUY", "symbol": pairs['t1'][i], "volume": shares_stock1})

                    # Description of our position
                    self.update_pairs({'t1': pairs['t1'][i],
                                       't2': pairs['t2'][i],
                                       'long': True,
                                       'shares_stock1': shares_stock1,
                                       'shares_stock2': shares_stock2,
                                       'active': True})

            # We have a position on a pair and therefore examine whether to close it
            else:
                # We previously bought the stock 1
                if pairs['long'][i]:
                    if z_score > 0:
                        # Sell stock 1 and buy back stock 2

                        # Send sell signal to main
                        self.notify_observers(
                            {"signal": "SELL", "symbol": pairs['t1'][i], "volume": pairs['shares_stock1'][i]})

                        # Send buy signal to main
                        self.notify_observers(
                            {"signal": "BUY", "symbol": pairs['t2'][i], "volume": pairs['shares_stock2'][i]})

                        # We close the position in the pair
                        self.update_pairs({'t1': pairs['t1'][i],
                                           't2': pairs['t2'][i],
                                           'long': '%s',
                                           'shares_stock1': None,
                                           'shares_stock2': None,
                                           'active': False})

                else:
                    if z_score < 0:
                        # Buy back stock 1 and sell stock 2

                        # Send buy signal to main
                        self.notify_observers(
                            {"signal": "BUY", "symbol": pairs['t1'][i], "volume": pairs['shares_stock1'][i]})

                        # Send sell signal to main
                        self.notify_observers(
                            {"signal": "SELL", "symbol": pairs['t2'][i], "volume": pairs['shares_stock2'][i]})

                        # We close the position in the pair
                        self.update_pairs({'t1': pairs['t1'][i],
                                           't2': pairs['t2'][i],
                                           'long': None,
                                           'shares_stock1': None,
                                           'shares_stock2': None,
                                           'active': False})
