import os
import sys
from IPython.display import display
import pandas as pd

A = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/A.csv'), sep=",")
AA = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/AA.csv'), sep=",")
AMZN = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/AMZN.csv'), sep=",")
AAPL = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/AAPL.csv'), sep=",")

frames = [A.Close, AA.Close, AMZN.Close, AAPL.Close]

result = pd.concat(frames)
# display(result)
data_df = pd.concat(
    frames,
    axis=1,
    join='inner',
    keys=['A', 'AA', 'AMZN', 'AAPL'],
)

data_df.to_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/hist_data.csv'),index=False,)

#hist_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'Algorithms/hist_data.csv'))

#display(hist_data)

