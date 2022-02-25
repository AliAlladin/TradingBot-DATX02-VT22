import backtrader as bt
import numpy as np
import statsmodels.api as sm


# Strategy 1
# Every strategy made needs to extend the base strategy, bt.Strategy class.
class Strategy_1(bt.Strategy):

    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.index = len(self.datas)-1
        self.currentIndex = 0
        self.dataclose = []
        for i in range(0,self.index+1):
            self.dataclose.append(self.datas[i].close)
        #self.dataclose = self.datas[self.index].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.order_pending = [None, None]
        self.buyprice = None
        self.buycomm = None
        self.bar_executed = [len(self), len(self)]



    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))



        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        #self.order = None

    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # Defines when to buy and sell
    def next(self):
        for i in range(0, self.index + 1):
            # Log the closing price of the series from the reference
            self.log('Close, %.2f' % self.dataclose[i][0])

            # Check if an order is pending ... if yes, we cannot send a 2nd one
            #if self.order:
                #return

            # Check if we are in the market
            if not self.getposition(self.datas[i]):  # Returns the current position for a given data in a given broker.

                # Not yet ... we MIGHT BUY if ...
                if self.dataclose[i][0] < self.dataclose[i][-1]:
                    # current close less than previous close

                    if self.dataclose[i][-1] < self.dataclose[i][-2]:
                        # previous close less than the previous close

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[i][0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy(self.datas[i])

            else: # Already in the market ... we might sell
                if self.dataclose[i][0] > self.dataclose[i][-1]:
                    # current close less than previous close

                    if self.dataclose[i][-1] > self.dataclose[i][-2]:

                        # SELL, SELL, SELL!!! (with all possible default parameters)
                        self.log('SELL CREATE, %.2f' % self.dataclose[i][0])

                        # Keep track of the created order to avoid a 2nd order

                        self.order = self.sell(self.datas[i])




#------------------------------------------------------------------------------------------



class Strategy_pair(bt.Strategy):


    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, dic):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dic = dic
        self.distance = 3
        self.long = None
        self.data_x =[]
        self.data_y = []
        self.dataclose = []
        for i in range(0,2):
            self.dataclose.append(self.datas[i].close)
        self.period = 300




    

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None




    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))



        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        #self.order = None

    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # Defines when to buy and sell
    def next(self):
        # Log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0][0])
        self.log('Close, %.2f' % self.dataclose[1][0])

        self.data_x.append(self.dataclose[0][0])
        self.data_y.append(self.dataclose[1][0])

        if len(self) > self.period:

            relevantXData = self.data_x[len(self) - self.period:len(self)]
            relevantYData = self.data_y[len(self) - self.period:len(self)]


            result = sm.OLS(relevantXData,relevantYData).fit()
            beta = result.params[0]
            spread = []
            for i in range(0,len(relevantXData)):
                spread.append(relevantXData[i] - beta *relevantYData[i])
            mean = np.mean(spread)
            std = np.std(spread)
            #p1 = adfuller(spread)[1]
            #p2 = coint(relevantXData, relevantYData)[1]
            zScore = (spread[self.period-1] - mean) /std

            currentRatio = relevantXData[self.period-1]/relevantYData[self.period-1]
            if currentRatio < 1:
                currentRatio = 1/currentRatio
                reversed = True
                # currentRatio = round(currentRatio)


            # Check if we are in the market
            if not self.getposition(self.datas[0]):  # Returns the current position for a given data in a given broker.
                if zScore > self.distance:
                    self.log('BUY CREATE, %.2f' % self.dataclose[1][0])
                    self.order = self.buy(self.datas[1],30)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0][0])
                    self.order = self.sell(self.datas[0],currentRatio*30)
                    self.long = False
                    self.lastRatio = currentRatio
                elif zScore < -self.distance:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0][0])
                    self.order = self.buy(self.datas[0],currentRatio*30)
                    self.log('SELL CREATE, %.2f' % self.dataclose[1][0])
                    self.order = self.sell(self.datas[1],30)
                    self.long = True
                    self.lastRatio = currentRatio

            else:
                if self.long:
                    if zScore > 0:
                        self.log('BUY CREATE, %.2f' % self.dataclose[1][0])
                        self.order = self.buy(self.datas[1],30)
                        self.log('SELL CREATE, %.2f' % self.dataclose[0][0])
                        self.order = self.sell(self.datas[0],self.lastRatio*30)
                else:
                    if zScore < 0:
                        self.log('BUY CREATE, %.2f' % self.dataclose[0][0])
                        self.order = self.buy(self.datas[0],self.lastRatio*30)
                        self.log('SELL CREATE, %.2f' % self.dataclose[1][0])
                        self.order = self.sell(self.datas[1],30)


#----------------------------------------------------------------------------------

class Strategy_pairGen(bt.Strategy):

    # "Self" is the bar/line we are on, of the data
    def log(self, txt, dt=None):
        # Logging function/output for this strategy
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, dic , pairs):
        self.dic = dic  # Dictionary of tickers with indices
        self.pairs = pairs  # List of pairs

        self.myData = {}  # To store all the data we need, {'TICKER' -> Data}
        for ticker in dic.keys():  # Initially, the values of data are just empty lists
            self.myData[ticker] = []

        # The parameters that are to be varied to optimize the model
        self.distance = 2.45
        self.period = 300

        # The closing data of the stocks
        self.dataclose = []
        for i in range(0, len(self.dic)):
            self.dataclose.append(self.datas[i].close)

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.opsize = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                '''
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                #self.buyprice = order.executed.price
                #self.buycomm = order.executed.comm
                #self.opsize = order.executed.size'''

            else:  # Sell
                '''self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))'''



        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        # self.order = None

    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # Defines when to buy and sell
    def next(self):
        for key in self.myData.keys():
            self.myData.get(key).append(self.dataclose[self.dic.get(key)][0])
        for pair in self.pairs:
            # Log the closing price of the series from the reference
            #self.log('Close, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
            #self.log('Close, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])

            if len(self) > self.period:

                relevantXData = self.myData.get(pair.stock1)[len(self) - self.period:len(self)]
                relevantYData = self.myData.get(pair.stock2)[len(self) - self.period:len(self)]

                result = sm.OLS(relevantXData, relevantYData).fit()
                beta = result.params[0]
                spread = []
                for i in range(0, len(relevantXData)):
                    spread.append(relevantXData[i] - beta * relevantYData[i])
                mean = np.mean(spread)
                std = np.std(spread)
                # p1 = adfuller(spread)[1]
                # p2 = coint(relevantXData, relevantYData)[1]
                zScore = (spread[self.period - 1] - mean) / std

                currentRatio = relevantXData[self.period - 1] / relevantYData[self.period - 1]
                sharesX = 10000/relevantXData[self.period - 1]


                # Check if we are in the market
                if not pair.isActive:  # Returns the current position for a given data in a given broker.
                    if zScore > self.distance:
                        print(zScore)
                        #self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                        self.order = self.sell(self.datas[self.dic.get(pair.stock1)],size = sharesX)
                        #self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                        self.order = self.buy(self.datas[self.dic.get(pair.stock2)], size = sharesX * currentRatio)
                        pair.long = False
                        pair.lastRatio = currentRatio
                        pair.sharesX = sharesX
                        pair.isActive = True



                    elif zScore < -self.distance:
                        print(zScore)
                       # self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                        self.order = self.sell(self.datas[self.dic.get(pair.stock2)], size = sharesX * currentRatio)
                        #self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                        self.order = self.buy(self.datas[self.dic.get(pair.stock1)],  size = sharesX)
                        pair.long = True
                        pair.sharesX = sharesX
                        pair.lastRatio = currentRatio
                        pair.isActive = True


                else:
                    if pair.long:
                        if zScore > 0:
                            print(zScore)
                            #self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                            self.order = self.sell(self.datas[self.dic.get(pair.stock1)], size = pair.sharesX)
                           # self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                            self.order = self.buy(self.datas[self.dic.get(pair.stock2)], size = pair.lastRatio * pair.sharesX)
                            pair.isActive = False

                    else:
                        if zScore < 0:
                            print(zScore)
                            #self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                            self.order = self.sell(self.datas[self.dic.get(pair.stock2)], size = pair.lastRatio * pair.sharesX)
                            #self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                            self.order = self.buy(self.datas[self.dic.get(pair.stock1)],size = pair.sharesX)
                            pair.isActive = False
