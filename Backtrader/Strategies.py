import backtrader as bt


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
        self.index = 1
        self.currentIndex = 0
        self.dataclose = []
        for i in range(0,self.index+1):
            self.dataclose.append(self.datas[i].close)
        #self.dataclose = self.datas[self.index].close

        # To keep track of pending orders and buy price/commission
        self.order = None
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

            self.bar_executed[self.currentIndex] = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

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
            if self.order:
                return

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
                        self.currentIndex = i
                        self.order = self.buy(self.datas[i])

            else:

                # Already in the market ... we might sell
                if len(self) >= (self.bar_executed[i] + 5):
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('SELL CREATE, %.2f' % self.dataclose[i][0])

                    # Keep track of the created order to avoid a 2nd order

                    self.currentIndex = i
                    self.order = self.sell(self.datas[i])


"""
#Stategy 2
class Strategy_1(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
"""
