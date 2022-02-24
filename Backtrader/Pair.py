class Pair:

    def __init__(self, stock1, stock2):
        self.stock1 = stock1
        self.stock2 = stock2
        self.sharesX = 0
        self.ratio = None
        self.long = None     # första aktien är long
        self.isActive = False