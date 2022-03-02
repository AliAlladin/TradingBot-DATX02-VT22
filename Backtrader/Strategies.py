import backtrader as bt
import numpy as np
import statsmodels.api as sm


# Strategy 1
# Every strategy made needs to extend the base strategy, bt.Strategy class.
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
        self.invested_amount = 10000
        # The closing data of the stocks
        self.dataclose = []
        for i in range(0, len(self.dic)):  # We add the closing data for each of all stocks
            self.dataclose.append(self.datas[i].close)

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
            if order.isbuy():'''
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                
                #self.buyprice = order.executed.price
                #self.buycomm = order.executed.comm
                #self.opsize = order.executed.size'''


            # It is a selling order
            else:'''
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))'''


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

        self.log('Close, %.2f' % self.dataclose[0][0])
        self.log('Close, %.2f' % self.dataclose[1][0])
        # For each stock, we add the data
        # Append today's stock price at the ticker's index to the initially emptly list
        for ticker in self.myData.keys():
            self.myData.get(ticker).append(self.dataclose[self.dic.get(ticker)][0])




    # We go through each pair
        for pair in self.pairs:

            # We want to only look after 'period' days
            if len(self) > self.period:

                # Sort to receive only data of the last 'period' days
                relevant_data_stock1 = self.myData.get(pair.stock1)[len(self) - self.period:len(self)]
                relevant_data_stock2 = self.myData.get(pair.stock2)[len(self) - self.period:len(self)]

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
                        self.order = self.sell(self.datas[self.dic.get(pair.stock2)], size=shares_stock1 * current_ratio)
                        # self.log('BUY CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock1)][0])
                        self.order = self.buy(self.datas[self.dic.get(pair.stock1)],  size=shares_stock1)


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
                            self.order = self.buy(self.datas[self.dic.get(pair.stock2)], size=pair.shares_stock1 * pair.ratio)

                            # Calculating the profit of the pairs trading
                            profit = pair.shares_stock1 * self.datas[self.dic.get(pair.stock1)] \
                                     - pair.shares_stock1 * pair.ratio * self.datas[self.dic.get(pair.stock2)]

                            # To log the profit and the pair
                            self.log('PROFIT: %.2f' % (profit) + '. TRADED PAIR: ' + pair.stock1 + ' AND ' + pair.stock2)

                            # We close the position in the pair
                            pair.isActive = False
                            pair.shares_stock1 = None
                            pair.ratio = None


                    else:

                        if z_score < 0:
                            # Buy back stock 1 and sell stock 2
                            # self.log('SELL CREATE, %.2f' % self.dataclose[self.dic.get(pair.stock2)][0])
                            self.order = self.sell(self.datas[self.dic.get(pair.stock2)], size=pair.ratio * pair.shares_stock1)
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