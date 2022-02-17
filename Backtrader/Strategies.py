import backtrader as bt


# Strategy 1
# Every strategy made needs to extend the base strategy, bt.Strategy class.
class Strategy_1(bt.Strategy):

    # Logging function
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))  # Print date and close

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        # Refers to the closing price which is accessed through datas[0].close or datas[0].open
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None  # Tells us if we're currently in a trade or if an order is pending
        self.buyprice = None
        self.buycomm = None

    # Where everything related to trade orders gets processed. Basically a tool for logging.
    def notify_order(self, order):

        # Buy/Sell order submitted/accepted to/by broker - Nothing to do
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():

                # If a order is completed and it is of a BUY-type, log its' execution
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     ))

                # Update variables
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            else:

                # If a order is completed and it is of a SELL-type, log its' execution
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        # If order did not go though, i.e canceled/rejected by broker, log it
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset order status: no pending order
        self.order = None

    # Receives a trade whenever there has been a change in one
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # Contains all sell/buy logic. Where we define the core of the strategy
    def next(self):
        # Log the closing price of each series
        self.log('Close, %.2f' % self.dataclose[0])

        # If we have a pending order... don't continue. (Specific for this strategy only)
        if self.order:
            return

        # Check if we are in the market
        if not self.position:  # Returns the current position for a given data in a given broker.

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close

                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close

                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

        # TODO: Should add CLOSE CREATE in order to check if we have any open trades


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
