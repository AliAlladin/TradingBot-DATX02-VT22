import pandas as pd

class Pair2:

    def __init__(self, stock1, stock2, p1):
        self.stock1 = stock1
        self.stock2 = stock2
        self.p1 = str(p1)
    def printP(self):
        print(self.stock1, " + ", self.stock2, "pvalues = ", self.p1)
    def getStockName(self):
        return self.stock1, self.stock2
    def toString(self):
        print(self.stock1,self.stock2,self.p1)

