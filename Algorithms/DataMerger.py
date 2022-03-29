"""
THIS FILE IS TO BE REMOVED ONCE FINISHED WITH. IT IS ONLY A HELPER CLASS FOR GENERATING DATAFRAMES.
"""

import os
import sys
from IPython.display import display
import pandas as pd

A = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/A.csv'), sep=",")
AA = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/AA.csv'), sep=",")
AAPL = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/AAPL.csv'), sep=",")
AMZN = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Data/AMZN.csv'), sep=",")

frames = [A.Date, A.Close, AA.Close, AAPL.Close, AMZN.Close]

result = pd.concat(frames)
# display(result)
data_df = pd.concat(
    frames,
    axis=1,
    join='inner',
    keys=['Date', 'A', 'AA', 'AAPL', 'AMZN'],
)

data_df.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/tempData.csv'), index=False, )

hist_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/tempData.csv'))

display(hist_data)
