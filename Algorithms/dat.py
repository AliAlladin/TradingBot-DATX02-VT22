# Import package
import os

import pandas as pd
import sys
# csv_data.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testdata.csv'), indecis=True)
import yfinance as yf

pd.options.mode.chained_assignment = None  # default='warn'

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# Get the csv_data
# csv_data = yf.download(tickers="AAPL A AA AMZN", period="7d", interval="1m")['Close']

'''
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
'''

'''
indices = []
for i in range(len(csv_data)):
    if csv_data.iloc[i]['DateTime'].time() == time(9, 30, 00):
        indices.append(i)
print(indices)
start_index = indices[len(indices) - 85]
print(start_index)

start_date = date.today() - timedelta(days=85)


for i in range(len(csv_data.index), 0, -1):
    # get row contents as series using iloc{] & index pos of row
    print(csv_data.iloc(i))
'''

'''
# start_date = date.today() - timedelta(days=365)
# print(start_date)
# days = np.busday_count(start_date, date.today()) * 390
# print(csv_data.index)

def extract_start_index(period: int):
    start_index = 0
    count = 0
    for i in range(len(csv_data.index) - 1, 0, -1):
        if csv_data.iloc[i]['DateTime'].time() == time(9, 30, 00):
            count += 1
            if count == period:
                start_index = i
                break
    return start_index


start_index = extract_start_index(85)
m = csv_data.iloc[start_index]['DateTime'].date()

csv_data = csv_data[start_index:]
print(csv_data)
'''
'''
csv_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/A.csv'))
csv_data['DateTime'] = pd.to_datetime(csv_data['DateTime'])

minute_data = yf.download(tickers="A", period="1d", interval="1m")
minute_data.reset_index(inplace=True)
latest = minute_data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
latest.rename(columns={'Datetime': 'DateTime'}, inplace=True)


lol = pd.concat([csv_data, latest])
print(lol)

lol.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/kkkkkkkkkkkkkk.csv'))
'''
hee = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/kkkkkkkkkkkkkk.csv'))
print(hee.iloc[-1])
