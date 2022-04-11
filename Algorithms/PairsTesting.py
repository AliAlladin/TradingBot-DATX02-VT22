import datetime
import os
import sys

import pandas as pd
from datetime import time, date
import pytz

from Algorithms.FibonacciTrading import FibonacciStrategy

csvFrame = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testingData.csv'))
minuteFrame = pd.DataFrame({'Symbol': ['AMZN', 'AA', 'AAP', 'A'], 'Price': [144, 14, 41, 84]})
'''
rows = csvFrame.columns[1:]
emptyRows = [0] * len(rows)
investments = pd.DataFrame({'Symbol': rows, 'Volume': emptyRows})
investments.sort_values(by='Symbol', inplace=True)
investments.loc[(investments.Symbol == 'A'), 'Volume'] = 500
print(investments)
'''

m = FibonacciStrategy(csvFrame)
m.run(minuteFrame)

# minuteFrame.sort_values(by='Symbol', inplace = True)


def updateFrame(csv, minuteBars):
    print(csv)
    dat = csv['DateTime']
    csv = csv.reindex(sorted(csvFrame.columns[1:]), axis=1)
    csv.insert(0, 'DateTime', dat)

    minuteBars.sort_values(by='Symbol', inplace=True)
    emptyRow = [0] * len(csv.columns)
    new_timezone = pytz.timezone("US/Eastern")
    csv.loc[len(csv.index)] = emptyRow
    csv.iloc[-1, 0] = datetime.datetime.now(new_timezone).strftime("%Y-%m-%d %H:%M:%S")

    for i in range(1, (len(csv.columns))):
        csv.iloc[-1, i] = minuteBars.iloc[i - 1]['Price']
    return csv

# k = updateFrame(csvFrame, minuteFrame)
# print(k)
