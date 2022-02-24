import pandas as pd

class Pair2:

    def __init__(self, stock1, stock2, beta, pVal):
        self.stock1 = stock1
        self.stock2 = stock2
        self.beta = beta
        self.pVal = pVal
    def printP(self):
        print(self.stock1, " + ", self.stock2, "pvalues = ", self.pVal)
    def getStockName(self):
        return self.stock1, self.stock2

