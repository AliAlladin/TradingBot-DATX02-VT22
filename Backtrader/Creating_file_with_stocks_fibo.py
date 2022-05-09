import os
import sys  # To find out the script name (in argv[0])

modpath = os.path.dirname(os.path.dirname(sys.argv[0]))  # Individual os paths


def creating_file_with_stocks():
    stocks = []
    directory_in_str = os.path.join(modpath, 'Data/filtered_csv_data/')
    directory = os.fsencode(directory_in_str)
    for filename in os.listdir(directory):
        x = (str(filename))
        x = x.split('\'')[1]
        x = x.removesuffix('.csv')
        stocks.append(x)
    my_pair_file = open('Stocks.txt', 'w')
    for i in stocks:
        my_pair_file.write(i + "\n")
    my_pair_file.close()
