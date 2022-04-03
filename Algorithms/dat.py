# Import package
import os
from datetime import time

import pandas as pd
import sys

# Get the data
# data = yf.download(tickers="AAPL A AA AMZN", period="7d", interval="1m")['Close']

# data.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testdata.csv'), indecis=True)

hist_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testdata.csv'))

hist_data['Datetime'] = pd.to_datetime(hist_data['Datetime'])

latest = hist_data.iloc[-1]['Datetime'].date()
length = len(hist_data['Datetime'])

# Collects all indices for when market opens
indices = []
for i in range(len(hist_data)):
    k = hist_data.iloc[i]['Datetime'].time()
    if k == time(9, 30, 00):
        indices.append(i)

start_index = indices[len(indices) - 2]
print(start_index)

print(hist_data[start_index:])