class Pair:

    def __init__(self, stock1, stock2):
        self.stock1 = stock1
        self.stock2 = stock2
        self.shares_stock1 = 0              # The number of shares of stock 1 that we will buy/sell
        self.ratio = None                   # The buy ratio between the two stock
        self.long = None                    # We are long the first stock
        self.isActive = False               # Whether we have a position of the pair in the market
