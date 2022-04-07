import numpy as np
import pandas as pd
import statsmodels.api as sm

pd.options.mode.chained_assignment = None  # default='warn'

'''
This class receives a dataframe containing the latest prices for each ticker.
It will go through each ticker, find its pair and perform the strategy on that pair in order
to check whether or not we should sell or buy a either of the stocks of that pair. In that case,
a sell/buy sigal will be passed back to Main.
'''


class PairsTrading:

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, signal: dict):
        for obs in self._observers:
            obs.notify(self, signal)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def __init__(self, pairs, distance, period, invested_amount):
        self.pairs = pairs
        self.pairs.columns = ['T1', 'T2']
        self.pairs['Active'] = False
        self.pairs['long'] = None
        self.pairs['shares_stock1'] = None
        self.pairs['shares_stock2'] = None


        self._observers = []  # List of observers to be notified

        # The parameters that are to be varied to optimize the model
        self.distance = distance
        self.period = period
        self.invested_amount = invested_amount

    def run(self, latest_prices: pd.DataFrame, hist_prices: pd.DataFrame):
        for i in range(len(self.pairs.index)):

            # Fetches a pair and the latest prices for each of the tickers
            t1 = self.pairs['T1'][i]  # Ticker symbol
            t2 = self.pairs['T2'][i]  # Ticker symbol

            # Latest minute data for ticker. Only 1 data point.
            tick1 = latest_prices.loc[latest_prices['Symbol'] == t1]
            tick2 = latest_prices.loc[latest_prices['Symbol'] == t2]

            '''
            Creates a new dataframe with only the historical closing prices for the specific pair.
            By default, the Alpaca API will return today's candle even though it is not closed. This is incomplete.
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
            if not self.pairs['Active'][i]:
                # We check whether the Z-score is unusually high or low (>distance or <-distance)
                if z_score > self.distance:
                    # High Z-score, we sell stock 1 and buy stock 2

                    # Send sell signal to main
                    shares_stock1 = round(shares_stock1)
                    self.notify_observers({"signal": "SELL", "symbol": self.pairs['T1'][i], "volume": shares_stock1})

                    shares_stock2 = shares_stock1 * current_ratio
                    # Send buy signal to main
                    self.notify_observers(
                        {"signal": "BUY", "symbol": self.pairs['T2'][i], "volume": shares_stock2})

                    # Description of our position
                    self.pairs['long'][i] = False
                    self.pairs['shares_stock1'][i] = shares_stock1
                    self.pairs['shares_stock2'][i] = shares_stock2
                    self.pairs['Active'][i] = True

                # The Z-score is unusually low, we buy stock1 and sell stock2
                elif z_score < -self.distance:

                    shares_stock2 = round(shares_stock1 * current_ratio)

                    # Send sell signal to main
                    self.notify_observers(
                        {"signal": "SELL", "symbol": self.pairs['T2'][i], "volume": shares_stock2})

                    shares_stock1 = (shares_stock2 / current_ratio)

                    # Send buy signal to main
                    self.notify_observers({"signal": "BUY", "symbol": self.pairs['T1'][i], "volume": shares_stock1})


                    # Description of our position
                    self.pairs['long'][i] = True
                    self.pairs['shares_stock1'][i] = shares_stock1
                    self.pairs['shares_stock2'][i] = shares_stock2
                    self.pairs['Active'][i] = True

            # We have a position on a pair and therefore examine whether to close it
            else:
                # We previously bought the stock 1
                if self.pairs['long'][i]:
                    if z_score > 0:
                        # Sell stock 1 and buy back stock 2

                        # Send sell signal to main
                        self.notify_observers(
                            {"signal": "SELL", "symbol": self.pairs['T1'][i], "volume": self.pairs['shares_stock1'][i]})

                        # Send buy signal to main
                        self.notify_observers({"signal": "BUY", "symbol": self.pairs['T2'][i],
                            "volume": self.pairs['shares_stock2'][i]})

                        # We close the position in the pair
                        self.pairs['shares_stock1'][i] = None
                        self.pairs['shares_stock2'][i] = None
                        self.pairs['Active'][i] = False

                else:
                    if z_score < 0:
                        # Buy back stock 1 and sell stock 2

                        # Send buy signal to main
                        self.notify_observers(
                            {"signal": "BUY", "symbol": self.pairs['T1'][i], "volume": self.pairs['shares_stock1'][i]})

                        # Send sell signal to main
                        self.notify_observers({"signal": "SELL", "symbol": self.pairs['T2'][i],
                            "volume": self.pairs['shares_stock2'][i]})

                        # We close the position in the pair
                        self.pairs['shares_stock1'][i] = None
                        self.pairs['shares_stock2'][i] = None
                        self.pairs['Active'][i] = False
