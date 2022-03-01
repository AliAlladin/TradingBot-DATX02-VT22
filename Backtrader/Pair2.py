import pandas as pd

class Pair2:

    def __init__(self, stock1, stock2, p1, p2):
        self.stock1 = stock1
        self.stock2 = stock2
        self.p1 = str(p1)
        self.p2 = str(p2)
    def printP(self):
        print(self.stock1, " + ", self.stock2, "pvalues = ", self.p1,self.p2)
    def getStockName(self):
        return self.stock1, self.stock2
    def toString(self):
        print(self.stock1,self.stock2,self.p1,self.p2)

