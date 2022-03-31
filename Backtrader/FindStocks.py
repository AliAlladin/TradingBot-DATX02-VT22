import os
import sys


# To create a .txt-file with all stocks with data
def creating_file_with_stocks():

    stocks = []  # Initially empty list of stocks

    # To find the correct data files
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    directory_in_str = os.path.join(modpath, 'Data/filtered_csv_data/')
    directory = os.fsencode(directory_in_str)

    # We go through every file and save the name of the stock
    for filename in os.listdir(directory):
        stock_name = get_stock_name(filename)
        stocks.append(stock_name)

    store_stocks(stocks)


# To get the correct format of the name
def get_stock_name(filename):
    stock_name = str(filename)
    stock_name = stock_name.split('\'')[1]
    stock_name = stock_name.removesuffix('.csv')
    return stock_name


# To write stocks from the list to a .txt-file
def store_stocks(stocks):
    my_pair_file = open('Stocks.txt', 'w')
    for stock in stocks:
        my_pair_file.write(stock + "\n")
    my_pair_file.close()


creating_file_with_stocks()
