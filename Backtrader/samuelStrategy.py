import backtrader as bt
import numpy as np
import statsmodels.api as sm
from Pair import *
import datetime

class Strategy(bt.Strategy):    

    def __init__(self, invested, period, todate, my_result_file): 
        self.invested_amount = invested #amount in each stock
        self.period=period
        self.oldDate = str(self.datas[0].datetime.date(0))
        self.todate = self.params.todate
        self.my_result_file=my_result_file

    def log(self, txt, dt=None):  # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.datetime(0)
        self.my_result_file.write('%s, %s' % (dt.isoformat(), txt))
        print('%s, %s' % (dt.isoformat(), txt))

    # Reports an order instance
    def notify_order(self, order):
        print("hej")
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

class Strategy_pairGen(Strategy):

    params = (('distance', None),
            ('period', None),
            ('invested',None),
            ('todate',None),
            ('my_result_file',None),)

    def __init__(self):
        Strategy.__init__(self, self.params.invested, self.params.period, self.params.todate, self.params.my_result_file)
        self.stock1Data=[]
        self.stock2Data=[]
        
        # The parameters that are to be varied to optimize the model
        self.distance = self.params.distance
        self.active=False             
        self.long = None

        #paramters to close position at end date
        self.sellOf = False

        # The closing data of the stock
        self.dataclose = []
        for i in range(0, 2):  # We add the closing data for each of all stocks
            self.dataclose.append(self.datas[i].close)
    

        print("initialising") #just for terminal

    def next(self):
        #check if last date so that we close positions
        if self.todate == self.datas[0].datetime.date(0):
            self.sellOf = True

        newPotentialDate = str(self.datas[0].datetime.date(0))

        if newPotentialDate != self.oldDate: #Checking if new day then add the closing price the day before
            self.oldDate = newPotentialDate
            self.stock1Data.append(self.dataclose[0][-1])
            self.stock2Data.append(self.dataclose[1][-1])

        # We want to only look after 'period' days
        if len(self.stock1Data) >= self.period:
            # Sort to receive only data of the last 'period' days
            relevant_data_stock1 = self.stock1Data[len(self.stock1Data) - self.period:len(
                self.stock1Data) - 1]
            relevant_data_stock2 = self.stock2Data[len(self.stock2Data) - self.period:len(
                self.stock2Data) - 1]
            relevant_data_stock1.append(self.dataclose[0][0])
            relevant_data_stock2.append(self.dataclose[1][0])


            z_score=self.linearRegression(relevant_data_stock1,relevant_data_stock2,self.period) #Want to calculate the z_score

            # To know how much we need to buy of each stock
            shares_stock1 = self.invested_amount / relevant_data_stock1[self.period - 1]
            current_ratio = relevant_data_stock1[self.period - 1] / relevant_data_stock2[self.period - 1]

            # If we don't have a position in this pair
            if not self.active:
                self.takingPosition(z_score, current_ratio, shares_stock1)

            # We have a position on a pair and therefore examine whether to close it
            else:
                self.closingPosition(z_score, current_ratio, shares_stock1)

    def takingPosition(self, z_score, current_ratio, shares_stock1):
    # We check whether the Z-score is unusually high or low (>distance or <-distance)
        if z_score > self.distance and not self.sellOf:

            # High Z-score, we sell stock 1 and buy stock 2
            # self.log('SELL CREATE, %.2f' % self.dataclose[0][0])
            self.order = self.sell(self.datas[0], size=shares_stock1)
            # self.log('BUY CREATE, %.2f' % self.dataclose[1][0])
            self.order = self.buy(self.datas[1], size=shares_stock1 * current_ratio)

            # Description of our position
            self.long = False  # Pair.long is true when we are long of the first stock
            self.ratio = current_ratio
            self.shares_stock1 = shares_stock1
            self.active = True

        # The Z-score is unusually low, we buy stock1 and sell stock2
        elif z_score < -self.distance and not self.sellOf:
            # self.log('SELL CREATE, %.2f' % self.dataclose[1][0])
            self.order = self.sell(self.datas[1],
                                    size=shares_stock1 * current_ratio)
            # self.log('BUY CREATE, %.2f' % self.dataclose[0][0])
            self.order = self.buy(self.datas[0], size=shares_stock1)

            # Description of our position
            self.long = True
            self.shares_stock1 = shares_stock1
            self.ratio = current_ratio
            self.active = True

    def closingPosition(self,z_score, current_ratio, shares_stock1):
        if self.long:
            if z_score > 0 or self.sellOf:
                self.order = self.close(self.datas[0])
                self.order = self.close(self.datas[1])
                self.active = False
        else:
            if z_score < 0 or self.sellOf:
                self.order = self.close(self.datas[1])
                self.order = self.close(self.datas[0])
                self.active = False

    def linearRegression(self, data1,data2,period):
        data1_log=np.log10(data1)
        data2_log=np.log10(data2)
        # Perform a linear regression to calculate the spread
        result = sm.OLS(data1_log, sm.add_constant(data2_log)).fit()
        beta = result.params[1]
        spread = []
        for i in range(0, period):
            spread.append(data1_log[i] - beta * data2_log[i])

        # Calculation of the Z-score
        mean = np.mean(spread)
        std = np.std(spread)
        z_score = (spread[period - 1] - mean) / std
        return z_score

class Strategy_fibonacci(bt.Strategy):

    params = (('stock_name', None),
            ('invested', None),
            ('period', None),
            ('todate', None),
            ('my_result_file', None))

    # Initialization of the strategy
    def __init__(self):

        Strategy.__init__(self, self.params.invested, self.params.period, self.params.todate, self.params.my_result_file)
        # Parameters
        self.invested_amount = self.params.invested  # The amount for which we invest
        self.period = self.params.period  # Period to determine swing high and swing low
        self.stock_name=self.params.stock_name
        # To store data for each ticker
        self.ratios = [0.382, 0.5, 0.618]  # The Fibonacci ratios
        self.myData = []  # To store all the data we need, {'TICKER' -> Data}
        self.invested_at_level = []  # To know if we are invested, {'TICKER' -> [boolean, boolean, boolean]}
        self.indexChangeOfDay=[] #To know which datapoints to include. We save at which datapoint new day occur
        self.invested_at_level = [False] * len(self.ratios) # Initially not invested
        self.dataclose = self.datas[0].close # We add the closing data for each of all stocks

    # The "run method", defines when to buy and sell
    def next(self):

        newPotentialDate = str(self.datas[0].datetime.date(0))
        if newPotentialDate != self.oldDate:
            self.oldDate = newPotentialDate
            self.indexChangeOfDay.append(len(self.myData))
        # Loop through of all tickers, the following is done for all of them
        
        self.myData.append(self.dataclose[0])

        # We want the last 'period' of data points, stored in relevant_data
        if len(self.indexChangeOfDay) >= self.period:
            rightDays=self.indexChangeOfDay[len(self.indexChangeOfDay)-self.period]
            relevant_data = self.myData[rightDays:]

            # We take the prices of the current point and maximum and minimum on the period.
            price_now = relevant_data[-1]
            high = max(relevant_data)
            low = min(relevant_data)

            # The date of swing high and swing low
            date_high = np.argmax(relevant_data)
            date_low = np.argmin(relevant_data)

            # Are we in an uptrend or a downtrend?
            if date_high > date_low:
                uptrend = True # We are in an uptrend
                # We calculate the Fibonacci support levels
                fibonacci_levels = [high - (high - low) * ratio for ratio in self.ratios]

            else:
                uptrend = False  # We are in a downtrend

            # If we are in an uptrend, we want to buy the stocks at drawbacks (Fibonacci supports).
            if date_high > date_low:
            # We check if we have reached the Fibonacci support levels  
                for level in range(len(self.ratios)):
                    if price_now < fibonacci_levels[level] and not self.invested_at_level[level]:
                        # We have reached the level, so we buy some stocks
                        number_of_stocks = self.invested_amount / price_now
                        self.order = self.buy(self.datas[0], size = number_of_stocks)

                        # We do not want to buy on consecutive days, so we say that we have invested in this level
                        self.invested_at_level[level] = True

                # WHEN TO SELL? We sell when the stock price is at a new high on the period
                if price_now == high and self.invested_at_level.count(True) > 0:
                    # Sell all stocks, close the position
                    self.order = self.close(self.datas[0])
                    # We do not longer have a position in the ticker
                    for i in range(self.invested_at_level.count(True)):
                        self.invested_at_level[i] = False

            # We are in a downtrend, we therefore sell to avoid losing too much money
            else: #Not uptrend
                if price_now == low and self.invested_at_level.count(True) > 0:
                    # Sell all stocks, close the position
                    self.order = self.close(self.datas[0])
                    # We do not longer have a position in the ticker
                    for i in range(self.invested_at_level.count(True)):
                        self.invested_at_level[i] = False