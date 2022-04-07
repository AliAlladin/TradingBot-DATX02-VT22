"""
THIS FILE IS TO BE REMOVED ONCE FINISHED WITH. IT IS ONLY A HELPER CLASS FOR GENERATING DATAFRAMES.
"""

import os
import sys
from IPython.display import display
import pandas as pd
# Import package
import os
import yfinance as yf
from datetime import date, datetime
import sys
from time import sleep

# data = yf.download(tickers="A AA AAP AMZN", period="3d", interval="1m")['Close']
# data.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/muu.csv'))

'''
A = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/A.csv'), sep=",")
AA = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/AA.csv'), sep=",")
AAP = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/AAP.csv'), sep=",")
AMZN = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/AMZN.csv'), sep=",")

#tickers = [A, AA, AAP, AMZN]
#lengths = [len(A.index),len(AA.index),len(AAP.index),len(AMZN.index)]
#print(lengths)

frames = [AA.DateTime, A.Close, AA.Close, AAP.Close, AMZN.Close]

data_df = pd.concat(
    frames,
    axis=1,
    join='inner',
    keys=['DateTime', 'A', 'AA', 'AAP', 'AMZN'],
)

data_df.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testingData.csv'), index=False)
       # If we have begun a new date
       if date.today() != self.latest_csv_date:
           start_index = extract_start_index(self.period)

       
       # Collects all indices for when market opens
       indices = []
       for i in range(len(self.data)):
           if self.data.iloc[i]['Datetime'].time() == time(9, 30, 00):
               indices.append(i)

       start_index = indices[len(indices) - self.period]

#hist_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/tempData.csv'))

#display(hist_data)

# csv_data.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testdata.csv'), indecis=True)

pd.options.mode.chained_assignment = None  # default='warn'
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# Get the csv_data
# csv_data = yf.download(tickers="AAPL A AA AMZN", period="7d", interval="1m")['Close']


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

csv_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/A.csv'))
csv_data['DateTime'] = pd.to_datetime(csv_data['DateTime'])

minute_data = yf.download(tickers="A", period="1d", interval="1m")
minute_data.reset_index(inplace=True)
latest = minute_data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
latest.rename(columns={'Datetime': 'DateTime'}, inplace=True)


lol = pd.concat([csv_data, latest])
print(lol)

lol.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/kkkkkkkkkkkkkk.csv'))

# hee = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/kkkkkkkkkkkkkk.csv'))
# print(hee.iloc[-1])

csv_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/testData/A.csv'))
csv_data['DateTime'] = pd.to_datetime(csv_data['DateTime'])

def extract_start_index(df, period:int):
    start_index = 0
    count = 0
    for i in range(len(df.index) - 1, 0, -1):
        if count == period:
            break
        index_date = df.iloc[i]['DateTime'].date()
        if df.iloc[i - 1]['DateTime'].date() != index_date:
            count += 1
            start_index = i
    return start_index

print(csv_data)
mu = extract_start_index(csv_data, 3)
print(mu)
print(csv_data.iloc[mu]['DateTime'])

print(minute_data)
#updated_frame = pd.concat([csv_data, minute_data], axis=0)
#print(minute_data)
#print(updated_frame)
#csv_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testingData.csv'))

minute_data = yf.download(tickers="A AA AAP AMZN", period="1d", interval="1m")
minute_data.reset_index(inplace=True)
minute_data = minute_data[['Datetime', 'Close']]
#minute_data.rename(columns={'Datetime': 'DateTime'}, inplace=True)
#print( csv_data)

'''
'''
data = yf.download(tickers="A AA AAP AMZN", period="3d", interval="1m")['Close']
data.reset_index(inplace=True)
data = data[['Datetime', 'Close']]
data.rename(columns={'Datetime': 'DateTime'}, inplace=True)

testCSV = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testData.csv'))
print(data)
updated_frame = pd.concat([testCSV, data], axis=0)
print(updated_frame)
'''
'''
def extract_start_index(df, period:int):
    start_index = 0
    count = 0
    for i in range(len(df.index) - 1, 0, -1):
        if count == period:
            break
        index_date = df.iloc[i]['DateTime'].date()
        if df.iloc[i - 1]['DateTime'].date() != index_date:
            count += 1
            start_index = i
    return start_index

testCSV = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testData.csv'))
testCSV['DateTime'] = pd.to_datetime(testCSV['DateTime'])


if testCSV.iloc[-1]['DateTime'].date() != updated_frame.iloc[-1]['DateTime'].date():
    index = extract_start_index(updated_frame, 7)
    updated_frame= updated_frame[index:]

testCSV = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testData.csv'))
testCSV['DateTime'] = pd.to_datetime(testCSV['DateTime'])
print(testCSV)

testCSV.drop(0, inplace = True, axis=0)
testCSV.reset_index(inplace = True, drop=True)

print(testCSV)
'''
testCSV = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/testData.csv'))
testCSV['DateTime'] = pd.to_datetime(testCSV['DateTime'])
updated_frame = testCSV
for i in range(0, 5):
    minute = yf.download(tickers="A AA AAP AMZN", period="3d", interval="1m")['Close']
    minute.reset_index(inplace=True)
    minute.rename(columns={'Datetime': 'DateTime'}, inplace=True)
    updated_frame = pd.concat([updated_frame, minute], axis=0)
    updated_frame.drop(0, inplace=True, axis=0)
    updated_frame.reset_index(inplace=True, drop=True)
    print(updated_frame)
    sleep(60)