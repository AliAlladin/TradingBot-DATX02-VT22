import datetime
import os  # Get the right pathway here
import random

import sys  # To find out the script name (in argv[0])


def acquire_stocks():
    # To create the directory for which we read the ticker names.
    modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
    directory_in_str = os.path.join(modpath, 'Data/filtered_csv_data/')
    directory = os.fsencode(directory_in_str)

    # For each .csv-file, we read the stock name and append it do a list.
    stocks = []
    for filename in os.listdir(directory):
        x = (str(filename))
        x = x.split('\'')[1]
        x = x.removesuffix('.csv')

        stocks.append(x)
    return stocks


def store_stocks(stocks, textfile):
    # We open the file, write each stock on its own line
    file = open(textfile, 'w')
    for stock in stocks:
        file.write(stock + "\n")
    file.close()


def in_csv_file(start):
    my_stock_file = open('StocksAll.txt', 'r')
    priority_list = []
    not_priority = []

    for stock in my_stock_file:
        priority = True  # We assume that the date exists

        # The path to find the stock
        modpath = os.path.dirname(os.path.dirname(sys.argv[0]))
        stock = stock.split()[0]
        datap = os.path.join(modpath, 'Data/filtered_csv_data/{}.csv').format(stock)
        print(stock)

        # We open the stocks file and read the second line, which contains the first date.
        csv_file = open(datap, 'r')
        line = csv_file.readlines()[1]
        date = line.split()[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        # If the start of the .csv-file is later than our starting point for a stock, the pair is not prioritized
        if date > start:
            priority = False
        csv_file.close()

        if priority:
            priority_list.append(stock)
        else:
            not_priority.append(stock)

    my_stock_file.close()
    random.shuffle(priority_list)
    random.shuffle(not_priority)

    # We write the sorted list of pairs to a .txt-file
    total_list = priority_list + not_priority
    store_stocks(total_list, 'StocksPrioritized.txt')


def main():
    start_time = datetime.date(2007, 9, 7)
    stocks = acquire_stocks()
    store_stocks(stocks, 'StocksAll.txt')
    in_csv_file(start_time)


main()
