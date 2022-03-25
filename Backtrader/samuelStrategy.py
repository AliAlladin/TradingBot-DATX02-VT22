import backtrader as bt
import numpy as np
import statsmodels.api as sm
from Pair import *
import datetime


class Strategy_pairGen(bt.Strategy):
    params = (('distance', None),
              ('period', None),
              ('stock1',None),
              ('stock2',None),)

    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy{'A': 0, 'AA': 1}
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, stock1, stock2):
        self.stock1Data=[]
        self.stock2Data=[]
        
        # The parameters that are to be varied to optimize the model
        self.distance = self.params.distance
        self.period = self.params.period
        self.stock1=self.params.stock1
        self.stock2=self.params.stock2

        self.active=False
        self.ratio = None              
        self.long = None    
        self.shares_stock1 = 0                 
        #amount in each pair
        self.invested_amount = self.params.invested

        #paramters to close position at end date
        self.todate = self.params.todate
        self.sellOf = False

        #just for terminal
        print("initialising")

        # The closing data of the stock
        self.dataclose = []
        for i in range(0, 2):  # We add the closing data for each of all stocks
            self.dataclose.append(self.datas[i].close)
        self.oldDate = str(self.datas[0].datetime.date(0))
        self.firstTime = True

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
        #check if last date so that we close positions
        if self.todate == self.datas[0].datetime.date(0):
            self.sellOf = True


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
            self.stock1Data.append(self.dataclose[0][-1])
            self.stock1Data.append(self.dataclose[1][-1])
        # We go through each pair

        # We want to only look after 'period' days
        if len(self.stock1Data) >= self.period:
            # Sort to receive only data of the last 'period' days
            relevant_data_stock1 = self.stock1Data[len(self.stock1Data) - self.period:len(
                self.stock1Data) - 1]
            relevant_data_stock2 = self.stock2Data[len(self.stock2Data) - self.period:len(
                self.stock2Data) - 1]
            relevant_data_stock1.append(self.dataclose[0][0])
            relevant_data_stock2.append(self.dataclose[1][0])


            z_score=linearRegression(relevant_data_stock1,relevant_data_stock2,self.period) #Want to calculate the z_score

            # To know how much we need to buy of each stock
            shares_stock1 = self.invested_amount / relevant_data_stock1[self.period - 1]
            current_ratio = relevant_data_stock1[self.period - 1] / relevant_data_stock2[self.period - 1]

            # If we don't have a position in this pair
            if not self.active:
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

                    self.isActive = True

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
                    self.isActive = True

            # We have a position on a pair and therefore examine whether to close it
            else:
                # We previously bought the stock 1
                if self.long:
                    if z_score > 0 or self.sellOf:
                        print(self.sellOf)
                        # Sell stock 1 and buy back stock 2
                        # self.log('SELL CREATE, %.2f' % self.dataclose[0][0])
                        self.order = self.sell(self.datas[0], size=self.shares_stock1)
                        # self.log('BUY CREATE, %.2f' % self.dataclose[1][0])
                        self.order = self.buy(self.datas[1],
                                                size=self.shares_stock1 * self.ratio)

                        # Calculating the profit of the pairs trading
                        profit = self.shares_stock1 * self.datas[0] \
                                    - self.shares_stock1 * self.ratio * self.datas[1]

                        # To log the profit and the pair
                        self.log(
                            'PROFIT: %.2f' % (profit) + '. TRADED PAIR: ' + self.stock1 + ' AND ' + self.stock2)

                        # We close the position in the pair
                        self.isActive = False
                        self.shares_stock1 = None
                        self.ratio = None


                else:
                    if z_score < 0 or self.sellOf:
                        # Buy back stock 1 and sell stock 2
                        # self.log('SELL CREATE, %.2f' % self.dataclose[1][0])
                        self.order = self.sell(self.datas[1],
                                                size=self.ratio * self.shares_stock1)
                        # self.log('BUY CREATE, %.2f' % self.dataclose[0][0])
                        self.order = self.buy(self.datas[0], size=self.shares_stock1)

                        # Calculating the profit of the pairs trading
                        profit = self.shares_stock1 * self.ratio * self.datas[1] \
                                    - self.shares_stock1 * self.datas[0]

                        # To log the profit and the pair
                        self.log(
                            'PROFIT: %.2f' % (profit) + '. TRADED PAIR: ' + self.stock1 + ' AND ' + self.stock2)

                        # We close the position in the pair
                        self.isActive = False
                        self.shares_stock1 = None
                        self.ratio = None

def linearRegression(data1,data2,period):
        data1_log=np.log10(data1)
        relevant_data_stock2Log=np.log10(data2)
        # Perform a linear regression to calculate the spread
        result = sm.OLS(data1_log, sm.add_constant(relevant_data_stock2Log)).fit()
        beta = result.params[1]
        spread = []
        for i in range(0, period):
            spread.append(data1_log[i] - beta * relevant_data_stock2Log[i])

        # Calculation of the Z-score
        mean = np.mean(spread)
        std = np.std(spread)

        z_score = (spread[period - 1] - mean) / std
        return z_score