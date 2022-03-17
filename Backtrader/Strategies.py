import backtrader as bt
import numpy as np
import statsmodels.api as sm


class Strategy_pairGen(bt.Strategy):
    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self, dic, pairs):

        self.dic = dic  # Dictionary of tickers with indices
        self.pairs = pairs  # List of pairs
        self.myData = {}  # To store all the data we need, {'TICKER' -> Data}
        for ticker in dic.keys():  # Initially, the values of data are just empty lists
            self.myData[ticker] = []

        # The parameters that are to be varied to optimize the model
        self.distance = 3
        self.period = 500
        self.invested_amount = 10000
        # The closing data of the stocks
        self.dataclose = []
        for i in range(0, len(self.dic)):  # We add the closing data for each of all stocks len(self.dic)
            self.dataclose.append(self.datas[i].close)
        self.oldDate = str(self.datas[0].datetime.date(0))
        self.firstTime = True
        ''' This might be unnecessary 
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.opsize = None
        '''
    # Reports an order instance
    def notify_order(self, order):

        # The order is completed
        # Attention: broker could reject order if there is not enough cash
        if order.status in [order.Completed]:
            # If it is a buying order
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                # self.buyprice = order.executed.price
                # self.buycomm = order.executed.comm
                # self.opsize = order.executed.size


            # It is a selling order
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))


        # If the order is canceled, margin or rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        # We log the profit when we have completed a trade
        # TODO: This needs to be changed

        # self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
        #         (trade.pnl, trade.pnlcomm))
    # The "run method", defines when to buy and sell
    def next(self):

        # self.log('Close, %.2f' % self.dataclose[0][0])
        # self.log('Close, %.2f' % self.dataclose[1][0])
        # For each stock, we add the data
        # Append today's stock price at the ticker's index to the initially emptly list
        if self.firstTime:
            self.oldDate = str(self.datas[0].datetime.date(0))
            self.firstTime = False
        newPotentialDate = str(self.datas[0].datetime.date(0))
        if newPotentialDate != self.oldDate:
            self.oldDate = newPotentialDate
            print(self.oldDate)
            for ticker in self.myData.keys():
                self.myData.get(ticker).append(self.dataclose[self.dic.get(ticker)][0])

        # We go through each pair
        for pair in self.pairs:
            # We want to only look after 'period' days
            if len(self.myData.get(pair.stock1)) > self.period:
                # Sort to receive only data of the last 'period' days
                relevant_data_stock1 = self.myData.get(pair.stock1)[len(self.myData.get(pair.stock1)) - self.period:len(
                    self.myData.get(pair.stock1)) - 1]
                relevant_data_stock2 = self.myData.get(pair.stock2)[len(self.myData.get(pair.stock2)) - self.period:len(
                    self.myData.get(pair.stock2)) - 1]
                relevant_data_stock1.append(self.dataclose[self.dic.get(pair.stock1)][0])
                relevant_data_stock2.append(self.dataclose[self.dic.get(pair.stock2)][0])
                # Perform a linear regression to calculate the spread
                result = sm.OLS(relevant_data_stock1, relevant_data_stock2).fit()
                beta = result.params[0]
                spread = []
                for i in range(0, self.period):
                    spread.append(relevant_data_stock1[i] - beta * relevant_data_stock2[i])

                # Calculation of the Z-score
                mean = np.mean(spread)
                std = np.std(spread)

                z_score = (spread[self.period - 1] - mean) / std

                # To know how much we need to buy of each stock
                shares_stock1 = self.invested_amount / relevant_data_stock1[self.period - 1]
                current_ratio = relevant_data_stock1[self.period - 1] / relevant_data_stock2[self.period - 1]

                # If we don't have a position in this pair
                if not pair.isActive:
                    # We check whether the Z-score is unusually high or low (>distance or <-distance)
                    if z_score > self.distance:

                        # High Z-score, we sell stock 1 and buy stock 2
                        # self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                        self.order = self.sell(self.datas[self.dic.get(pair.stock1)], size=shares_stock1)
                        # self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                        self.order = self.buy(self.datas[self.dic.get(pair.stock2)], size=shares_stock1 * current_ratio)

                        # Description of our position
                        pair.long = False  # Pair.long is true when we are long of the first stock
                        pair.ratio = current_ratio
                        pair.shares_stock1 = shares_stock1

                        pair.isActive = True

                    # The Z-score is unusually low, we buy stock1 and sell stock2
                    elif z_score < -self.distance:
                        # self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                        self.order = self.sell(self.datas[self.dic.get(pair.stock2)],
                                               size=shares_stock1 * current_ratio)
                        # self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                        self.order = self.buy(self.datas[self.dic.get(pair.stock1)], size=shares_stock1)

                        # Description of our position
                        pair.long = True
                        pair.shares_stock1 = shares_stock1
                        pair.ratio = current_ratio
                        pair.isActive = True

                # We have a position on a pair and therefore examine whether to close it
                else:
                    # We previously bought the stock 1
                    if pair.long:

                        if z_score > 0:
                            # Sell stock 1 and buy back stock 2
                            # self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                            self.order = self.sell(self.datas[self.dic.get(pair.stock1)], size=pair.shares_stock1)
                            # self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                            self.order = self.buy(self.datas[self.dic.get(pair.stock2)],
                                                  size=pair.shares_stock1 * pair.ratio)

                            # Calculating the profit of the pairs trading
                            profit = pair.shares_stock1 * self.datas[self.dic.get(pair.stock1)] \
                                     - pair.shares_stock1 * pair.ratio * self.datas[self.dic.get(pair.stock2)]

                            # To log the profit and the pair
                            self.log(
                                'PROFIT: %.2f' % (profit) + '. TRADED PAIR: ' + pair.stock1 + ' AND ' + pair.stock2)

                            # We close the position in the pair
                            pair.isActive = False
                            pair.shares_stock1 = None
                            pair.ratio = None


                    else:

                        if z_score < 0:
                            # Buy back stock 1 and sell stock 2
                            # self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                            self.order = self.sell(self.datas[self.dic.get(pair.stock2)],
                                                   size=pair.ratio * pair.shares_stock1)
                            # self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                            self.order = self.buy(self.datas[self.dic.get(pair.stock1)], size=pair.shares_stock1)

                            # Calculating the profit of the pairs trading
                            profit = pair.shares_stock1 * pair.ratio * self.datas[self.dic.get(pair.stock2)] \
                                     - pair.shares_stock1 * self.datas[self.dic.get(pair.stock1)]

                            # To log the profit and the pair
                            self.log(
                                'PROFIT: %.2f' % (profit) + '. TRADED PAIR: ' + pair.stock1 + ' AND ' + pair.stock2)

                            # We close the position in the pair
                            pair.isActive = False
                            pair.shares_stock1 = None
                            pair.ratio = None

class Strategy_fibonacci(bt.Strategy):

    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # Initialization of the strategy
    def __init__(self, dic):

        self.dic = dic  # Dictionary of tickers with indices {'TICKER' -> Index}
        # Sets that store the highs and lows of the stock price
        self.highs = {}  # {'TICKER' -> HIGH}
        self.lows = {}  # {'TICKER' -> LOW}
        # Sets that store the dates of the highs and lows of the stock price {'TICKER' -> DATE}
        # TODO: We might remove the dates, they could be unnecessary.
        self.date_high = {}
        self.date_low = {}

        # We initialize these dictionaries
        for ticker in dic.keys():
            # Initialization of the highs and lows for the stock 'ticker'
            self.highs[ticker] = -1
            self.lows[ticker] = float('inf')
            '''
            self.date_high[ticker] = self.datas[0].datetime.datetime(0)
            self.date_low[ticker] = self.datas[0].datetime.datetime(0)
            '''

        # The closing data of the stocks
        self.dataclose = []
        for i in range(0, len(self.dic)):  # We add the closing data for each of all stocks
            self.dataclose.append(self.datas[i].close)

        # The parameters that are to be varied to optimize the model
        self.invested_amount = 10000  # The amount for which we invest
        self.ratios = [0.382, 0.5, 0.618]  # The Fibonacci ratios
        self.invested_at_level = [False] * len(self.ratios) # Initially no position in any stock

        # Variables that are needed for startup.
        self.startup = 0
        self.can_run = False

        # To localize if we are in an uptrend or in a downtrend
        self.uptrend = None

    # Reports an order instance
    def notify_order(self, order):
        # The order is completed
        # Attention: broker could reject order if there is not enough cash
        if order.status in [order.Completed]:
            # If it is a buying order
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            # It is a selling order
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))


        # If the order is canceled, margin or rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

    # The "run method", defines when to buy and sell
    def next(self):

        # Since we compare with prices from two points ago, we need two days startup.
        # TODO: Determine how to define the high and low, should we have an interval or locate these extreme points in another way?
        if not self.can_run:
            self.startup = self.startup + 1
            if self.startup == 2:
                self.can_run = True


        if self.can_run:
            # Loop through of all tickers, the following is done for all of them
            for ticker in self.dic.keys():

                # We take the prices of the current point and the two previous points.
                price_now = self.dataclose[self.dic.get(ticker)][0]
                price_one_point_ago = self.dataclose[self.dic.get(ticker)][-1]
                price_two_points_ago = self.dataclose[self.dic.get(ticker)][-2]

                # We recognize the swing high
                if price_one_point_ago > price_two_points_ago and price_one_point_ago > price_now and price_one_point_ago > self.highs[ticker]:
                    self.highs[ticker] = price_one_point_ago # Price of the swing high
                    self.date_high[ticker] = self.datas[0].datetime.datetime(-1) # Date of the swing high
                    # We calculate the Fibonacci support levels
                    high = self.highs.get(ticker)
                    low = self.lows.get(ticker)
                    self.fibonacci_levels = [high - (high - low) * ratio for ratio in self.ratios]
                    self.uptrend = True # We are in an uptrend
                # We recognize the swing low
                elif price_one_point_ago < price_two_points_ago and price_one_point_ago < price_now and price_one_point_ago < self.lows[ticker]:
                    self.lows[ticker] = price_one_point_ago # Price of the swing low
                    self.date_low[ticker] = self.datas[0].datetime.datetime(-1) # Price of the swing high
                    # We calculate the Fibonacci resistance levels
                    high = self.highs.get(ticker)
                    low = self.lows.get(ticker)
                    self.fibonacci_levels = [low + (high - low) * ratio for ratio in self.ratios]
                    self.uptrend = False # We are in a downtrend

                # If we are in an uptrend, we want to buy the stocks at drawbacks (Fibonacci supports).
                if self.uptrend:
                    # We check if we have reached the Fibonacci support levels
                    for level in range(len(self.ratios)):
                        if price_now < self.fibonacci_levels[level] and not self.invested_at_level[level]:
                            # We have reached the level, so we buy some stocks
                            number_of_stocks = self.invested_amount / price_now
                            self.order = self.buy(self.datas[self.dic.get(ticker)], size = number_of_stocks)

                            # We do not want to buy on consecutive days, so we say that we have invested in this level
                            self.invested_at_level[level] = True

                    # WHEN TO SELL? We sell when the stock price is at a new high again
                    if price_now == self.highs.get(ticker) and self.invested_at_level.count(True) > 0:
                        # Sell all stocks, close the position
                        self.order = self.close(self.datas[self.dic.get(ticker)])

                        # How many times have we 'bought the dip'? We close every position.
                        for i in range(self.invested_at_level.count(True)):
                            self.invested_at_level[i] = False

                    # TODO: Should we have some kind of stop loss?

                # TODO: Should we be able to short stocks if we are in a downtrend?
                '''
                if self.uptrend == False:
                    # We check if we have reached the Fibonacci resistance levels
                    for level in range(len(self.ratios)):
                        if price_now > self.fibonacci_levels[level] and not self.invested_at_level[level]:
                            # We have reached the level, so we short some stocks
                            number_of_stocks = self.invested_amount / price_now
                            self.order = self.sell(self.datas[self.dic.get(ticker)], size=number_of_stocks)

                            # We do not want to buy on consecutive days, so we say that we have invested in this level
                            self.invested_at_level[level] = True

                    # WHEN TO SELL? We buy back when the stock price is at a new low again
                    if price_now == self.lows.get(ticker) and self.invested_at_level.count(True) > 0:
                        # Buy back all stocks, close the position
                        self.order = self.close(self.datas[self.dic.get(ticker)])

                        # How many times have we shorted the stocks? We close every position.
                        for i in range(self.invested_at_level.count(True)):
                            self.invested_at_level[i] = False
                '''


class Strategy_fibonacci2(bt.Strategy):

    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # Initialization of the strategy
    def __init__(self, dic):

        self.dic = dic  # Dictionary of tickers with indices {'TICKER' -> Index}
        self.myData = {}  # To store all the data we need, {'TICKER' -> Data}
        # Sets that store the highs and lows of the stock price
        self.highs = {}  # {'TICKER' -> HIGH}
        self.lows = {}  # {'TICKER' -> LOW}
        # Sets that store the dates of the highs and lows of the stock price {'TICKER' -> DATE}
        # TODO: We might remove the dates, they could be unnecessary.
        self.date_high = {}
        self.date_low = {}

        # We initialize these dictionaries
        for ticker in dic.keys():
            self.myData[ticker] = [] # To store the stock prices
            # Initialization of the highs and lows for the stock 'ticker'
            self.highs[ticker] = -1
            self.lows[ticker] = float('inf')
            '''
            self.date_high[ticker] = self.datas[0].datetime.datetime(0)
            self.date_low[ticker] = self.datas[0].datetime.datetime(0)
            '''

        # The closing data of the stocks
        self.dataclose = []
        for i in range(0, len(self.dic)):  # We add the closing data for each of all stocks
            self.dataclose.append(self.datas[i].close)

        # The parameters that are to be varied to optimize the model
        self.invested_amount = 10000  # The amount for which we invest
        self.ratios = [0.382, 0.5, 0.618]  # The Fibonacci ratios
        self.invested_at_level = [False] * len(self.ratios) # Initially no position in any stock

        # Variables that are needed for startup.
        self.startup = 0
        self.can_run = False
        self.period = 10000

        # To localize if we are in an uptrend or in a downtrend
        self.uptrend = None

    # Reports an order instance
    def notify_order(self, order):
        # The order is completed
        # Attention: broker could reject order if there is not enough cash
        if order.status in [order.Completed]:
            # If it is a buying order
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            # It is a selling order
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))


        # If the order is canceled, margin or rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

    # The "run method", defines when to buy and sell
    def next(self):

        # Loop through of all tickers, the following is done for all of them
        for ticker in self.dic.keys():
            self.myData.get(ticker).append(self.dataclose[self.dic.get(ticker)][0])

            # We want the last 'period' of data points
            if len(self.myData.get(ticker)) > self.period:
                relevant_data = self.myData.get(ticker)[-self.period:]

                # We take the prices of the current point and the two previous points.
                price_now = relevant_data[-1]
                price_one_point_ago = relevant_data[-2]
                price_two_points_ago = relevant_data[-3]

                high = max(relevant_data)
                low = min(relevant_data)

                # We recognize the date of swing high and swing low
                date_high = np.argmax(relevant_data)
                date_low = np.argmin(relevant_data)

                # Are we in an uptrend or a downtrend?
                if date_high > date_low:
                    # We calculate the Fibonacci support levels
                    self.fibonacci_levels = [high - (high - low) * ratio for ratio in self.ratios]
                    self.uptrend = True # We are in an uptrend

                elif date_low > date_high:
                    self.fibonacci_levels = [low + (high - low) * ratio for ratio in self.ratios]
                    self.uptrend = False  # We are in a downtrend

                # If we are in an uptrend, we want to buy the stocks at drawbacks (Fibonacci supports).
                if self.uptrend:
                    # We check if we have reached the Fibonacci support levels
                    for level in range(len(self.ratios)):
                        if price_now < self.fibonacci_levels[level] and not self.invested_at_level[level]:
                            # We have reached the level, so we buy some stocks
                            number_of_stocks = self.invested_amount / price_now
                            self.order = self.buy(self.datas[self.dic.get(ticker)], size = number_of_stocks)

                            # We do not want to buy on consecutive days, so we say that we have invested in this level
                            self.invested_at_level[level] = True

                    # WHEN TO SELL? We sell when the stock price is at a new high again
                    if price_now == self.highs.get(ticker) and self.invested_at_level.count(True) > 0:
                        # Sell all stocks, close the position
                        self.order = self.close(self.datas[self.dic.get(ticker)])

                        # How many times have we 'bought the dip'? We close every position.
                        for i in range(self.invested_at_level.count(True)):
                            self.invested_at_level[i] = False

                    # TODO: Should we have some kind of stop loss?

                # TODO: Should we be able to short stocks if we are in a downtrend?
                '''
                if self.uptrend == False:
                    # We check if we have reached the Fibonacci resistance levels
                    for level in range(len(self.ratios)):
                        if price_now > self.fibonacci_levels[level] and not self.invested_at_level[level]:
                            # We have reached the level, so we short some stocks
                            number_of_stocks = self.invested_amount / price_now
                            self.order = self.sell(self.datas[self.dic.get(ticker)], size=number_of_stocks)
    
                            # We do not want to buy on consecutive days, so we say that we have invested in this level
                            self.invested_at_level[level] = True
    
                    # WHEN TO SELL? We buy back when the stock price is at a new low again
                    if price_now == self.lows.get(ticker) and self.invested_at_level.count(True) > 0:
                        # Buy back all stocks, close the position
                        self.order = self.close(self.datas[self.dic.get(ticker)])
    
                        # How many times have we shorted the stocks? We close every position.
                        for i in range(self.invested_at_level.count(True)):
                            self.invested_at_level[i] = False
                '''




