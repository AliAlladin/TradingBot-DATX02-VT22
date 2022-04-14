import backtrader as bt # The backtrader package
import numpy as np # So we can take the logarithm 
import statsmodels.api as sm # To make the linear regression
import datetime # To use dates

#General attributes for all strategies
class Strategy(bt.Strategy):    

    def __init__(self, invested, period, todate, my_result_file): 

        self.invested_amount = invested # Amount to invest in each stock
        self.period=period # Number of days before being able to analyse if buy/sell
        self.oldDate = str(self.datas[0].datetime.date(0)) # Variable to check if new date
        self.todate = self.params.todate # Variable so we sell on the last day (not necessary)
        self.my_result_file=my_result_file # File to save buys and sells so we can analyse afterwards
        self.sellOf = False # Variable to check if it is the last day

    def log(self, txt, dt=None):  # For saving important information

        dt = dt or self.datas[0].datetime.datetime(0) #If we want to give a specific date as input
        self.my_result_file.write('%s, %s' % (dt.isoformat(), txt+"\n")) # Saving the order information in the file
        print('%s %s ' % (dt.isoformat(), txt)) #To know what is happening during the time it is running

    # Reports an order instance
    def notify_order(self, order): # Backtrader calls this function

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

# Specific attributes pair trading
class Strategy_pairGen(Strategy): 

# The needed parameters
    params = (('stock1',None),
            ('stock2',None),
            ('distance', None),
            ('period', None),
            ('invested',None),
            ('todate',None),
            ('my_result_file',None),)

    def __init__(self):
       
       
        Strategy.__init__(self, self.params.invested, self.params.period, 
        self.params.todate, self.params.my_result_file) # Initiate the general parameters for any of the strategies

        # Name for the stocks

        self.stock1=self.params.stock1
        self.stock2=self.params.stock2

        # Saving stockdata for each stock
        self.stock1Data=[] 
        self.stock2Data=[]
        
        self.distance = self.params.distance # Distance from average
        self.active=False # To check if the pair is active             
        self.long = None # If we have bought the first stock or not

        # The closing data of the stock
        self.dataclose = []
        for i in range(0, 2):  # We add the closing data for each of all stocks
            self.dataclose.append(self.datas[i].close)
    
        self.firstTime=False # One thing we need to do the first time
        print("initialising") # Just for terminal

    def next(self):
        # Check if last date so that we close positions
        if self.todate == self.datas[0].datetime.date(0): # Check if last day (then we want to sell)
            self.sellOf = True

        if self.firstTime: #Hej
            self.oldDate = str(self.datas[0].datetime.date(0)) # We need the oldDate to be equal to the first day which cannot be initilized in init
            self.firstTime = False

        newPotentialDate = str(self.datas[0].datetime.date(0)) # Variable to check if it is new day

        if newPotentialDate != self.oldDate: # Checking if new day then add the closing price the day before
            self.oldDate = newPotentialDate
            self.stock1Data.append(self.dataclose[0][-1])
            self.stock2Data.append(self.dataclose[1][-1])

        # We want to only look after 'period' days
        if len(self.stock1Data) >= self.period: # To check if we can start making trades
            # Sort to receive only data of the last 'period' days

            # Extract relevant closing price for each stock
            relevant_data_stock1 = self.stock1Data[len(self.stock1Data) - self.period:] 
            relevant_data_stock2 = self.stock2Data[len(self.stock2Data) - self.period:]

            # Add the current price for each stock    
            relevant_data_stock1.append(self.dataclose[0][0])
            relevant_data_stock2.append(self.dataclose[1][0])

            z_score=self.linearRegression(relevant_data_stock1,relevant_data_stock2,self.period) # Want to calculate the z_score

            # To know how much we need to buy of each stock
            shares_stock1 = self.invested_amount / relevant_data_stock1[self.period - 1]
            current_ratio = relevant_data_stock1[self.period - 1] / relevant_data_stock2[self.period - 1]

            # If we don't have a position in this pair
            if not self.active:
                self.takingPosition(z_score, current_ratio, shares_stock1)

            # We have a position on a pair and therefore examine whether to close it
            else:
                self.closingPosition(z_score, current_ratio, shares_stock1)

    # To check whether to take a position or not
    def takingPosition(self, z_score, current_ratio, shares_stock1):
    # We check whether the Z-score is unusually high or low (>distance or <-distance)
        if z_score > self.distance and not self.sellOf:

            # High Z-score, we sell stock 1 and buy stock 2
            self.log('SELL CREATE at %.2f for stock: %s' % (self.dataclose[0][0], self.stock1))
            self.log('BUY CREATE at %.2f for stock: %s' % (self.dataclose[1][0], self.stock2))

            self.order = self.sell(self.datas[0], size=shares_stock1)
            self.order = self.buy(self.datas[1], size=shares_stock1 * current_ratio)

            # Description of our position
            self.long = False  # self.long is true when we are long the first stock
            self.active = True

        # The Z-score is unusually low, we buy stock1 and sell stock2
        elif z_score < -self.distance and not self.sellOf:
            
            self.log('SELL CREATE at %.2f for stock: %s' % (self.dataclose[1][0], self.stock1))
            self.log('BUY CREATE at %.2f for stock: %s' % (self.dataclose[0][0], self.stock2))
            
            self.order = self.sell(self.datas[1], size=shares_stock1 * current_ratio)
            self.order = self.buy(self.datas[0], size=shares_stock1)

            # Description of our position
            self.long = True
            self.active = True

    # To check whether or not we should close our poisition
    def closingPosition(self,z_score, current_ratio, shares_stock1):

        if self.long:
            if z_score > 0 or self.sellOf:
                self.log('SELL CREATE at %.2f for stock: %s' % (self.dataclose[0][0], self.stock1))
                self.log('BUY CREATE at %.2f for stock: %s' % (self.dataclose[1][0], self.stock2))

                self.order = self.close(self.datas[0])
                self.order = self.close(self.datas[1])
                
                self.active = False
        else:
            if z_score < 0 or self.sellOf:
                    
                self.log('SELL CREATE at %.2f for stock: %s' % (self.dataclose[1][0], self.stock1))
                self.log('BUY CREATE at %.2f for stock: %s' % (self.dataclose[0][0], self.stock2))
                
                self.order = self.close(self.datas[1])
                self.order = self.close(self.datas[0])
                
                self.active = False

    # Calculations the z-score for the pair
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

# The distinct class for the fibonacci strategy
class Strategy_fibonacci(Strategy):

    params = (('stock_name', None),
            ('invested', None),
            ('period', None),
            ('todate', None),
            ('my_result_file', None))

    # Initialization of the strategy
    def __init__(self):

        Strategy.__init__(self, self.params.invested, self.params.period, self.params.todate, 
        self.params.my_result_file) # The general parameters for any strategy
        
        # Parameters
        self.invested_amount = self.params.invested  # The amount for which we invest
        self.period = self.params.period  # Period to determine swing high and swing low
        self.stock_name=self.params.stock_name #The name of the stock
        
        # To store data for each ticker
        self.ratios = [0.382, 0.5, 0.618]  # The Fibonacci ratios
        self.myData = []  # To store all the data we up to this moment
        self.invested_at_level = []  # To know if we are invested [boolean, boolean, boolean]
        self.indexChangeOfDay=[] # To know which datapoints to include. We save at which datapoint new day occur
        self.invested_at_level = [False] * len(self.ratios) # Initially not invested
        self.dataclose = self.datas[0].close # We add the trading price for the stock

    # The "run method", defines when to buy and sell
    def next(self):

        newPotentialDate = str(self.datas[0].datetime.date(0))

        if newPotentialDate != self.oldDate: # Checking if new day
            self.oldDate = newPotentialDate
            self.indexChangeOfDay.append(len(self.myData))
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
                        self.log('Buy Created: Price: %.2f' %(self.dataclose[0]))

                        # We do not want to buy on consecutive days, so we say that we have invested in this level
                        self.invested_at_level[level] = True

                # WHEN TO SELL? We sell when the stock price is at a new high on the period
                if price_now == high and self.invested_at_level.count(True) > 0:
                    # Sell all stocks, close the position
                    self.order = self.close(self.datas[0])
                    self.log('Sell Created: Price: %.2f' %(self.dataclose[0]))
                    # We do not longer have a position in the ticker
                    for i in range(self.invested_at_level.count(True)):
                        self.invested_at_level[i] = False

            # We are in a downtrend, we therefore sell to avoid losing too much money
            else: #Not uptrend
                if price_now == low and self.invested_at_level.count(True) > 0:
                    # Sell all stocks, close the position
                    self.order = self.close(self.datas[0])
                    self.log('Sell Created: Price: %.2f' %(self.dataclose[0]))

                    # We do not longer have a position in the ticker
                    for i in range(self.invested_at_level.count(True)):
                        self.invested_at_level[i] = False

