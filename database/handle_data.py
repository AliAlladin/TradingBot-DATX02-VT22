import pandas as pd
import psycopg2
from sqlalchemy import create_engine


class DatabaseHandler:
    """
    This class sets up a connection to a postgres server on post 5432 and creates all tables, views and queries for
    a database that saves information for the pairs trading strategy.
    """

    def __init__(self):
        """
        Constructor for the class that sets up a connection to the database server and sets up required tables
        """

        self.conn = psycopg2.connect(
            host="localhost",
            database="tradingBot",
            user="postgres",
            password="postgres",
            port="5432"
        )

        self.engine = create_engine('postgresql://postgres:postgres@localhost:5432/tradingBot')

        self.cursor = self.conn.cursor()

        print("database Connected Successfully")

        cursor = self.conn.cursor()

        # drop
        # sql = open('../database/drop.sql', 'r')
        # cursor.execute(sql.read())
        # self.conn.commit()
        # print("drop table")

        # Tables
        sql = open('/tables.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("Table created")

        # Views
        sql = open('/views.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("views created")

    def insert_and_commit_query(self, stock_ticker: str, price: float, volume: float, query: str):
        """
        Inserts values into a query and executes to so that it is saved on the server
        :param stock_ticker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :param query: the query that is going to be committed to the server.
        :return: None
        """
        query = query.replace('a1', "\'" + stock_ticker + "\'")
        query = query.replace('a2', str(price))
        query = query.replace('a3', str(volume))
        self.cursor.execute(query)
        self.conn.commit()

    def sql_buy(self, stock_ticker: str, price: float, volume: float):
        """
        Saves information to the server if the system buys a stock
        :param stock_ticker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :return: None
        """
        query = "INSERT INTO Buy VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insert_and_commit_query(stock_ticker, price, volume, query)

    # inserts into sell
    def sql_sell(self, stock_ticker: str, price: float, volume: float):
        """
        Saves information to the server if the system sells a stock
        :param stock_ticker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :return: None
        """
        query = "INSERT INTO Sell VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insert_and_commit_query(stock_ticker, price, volume, query)

    # inserts into blank
    def sql_short(self, stock_ticker: str, price: float, volume: float):
        """
        Saves information to the server if the system shorts a stock
        :param stock_ticker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :return: None
        """
        query = "INSERT INTO Short VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insert_and_commit_query(stock_ticker, price, volume, query)

    # inserts into pairs
    def sql_pairs(self, stock_ticker_1: str, stock_ticker_2: str, standard_div: float):
        """
        Saves all the pairs in pair trading
        :param stock_ticker_1: stock name
        :param stock_ticker_2: stock name
        :param standard_div: value mismatch between each stock
        :return: None
        """
        query = "INSERT INTO Sell VALUES (a1 ,a2, a3)"
        query = query.replace('a1', "\'" + stock_ticker_1 + "\'")
        query = query.replace('a2', "\'" + stock_ticker_2 + "\'")
        query = query.replace('a3', str(standard_div))
        self.cursor.execute(query)
        self.conn.commit()

    def sql_update_price(self, stock_ticker: str, price: float):
        """
         Creates a table PriceF if it doesnt exist that saves the prices of all the stocks that are needed in fibonacci
         :param stock_ticker: name of a stock
         :param price: price of a stock
         :return: None
         """
        query = "INSERT INTO Prices (ticker, price) VALUES(a2, a1) ON CONFLICT (ticker) DO UPDATE SET price = a1 " \
                "WHERE Prices.ticker = a2 "
        query = query.replace('a1', str(price))
        query = query.replace('a2', "\'" + str(stock_ticker) + "\'")
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(stock_ticker)
            print(e)

    def sql_get_all_prices(self):
        """
        Returns all the values in PriceF which include stock names and the most recent price of that stock
        :return: Dataframe with all prices of all stocks in the database
        """
        try:
            postgresql_select_query = "select * from Prices"
            self.cursor.execute(postgresql_select_query)
            return pd.DataFrame.from_records(self.cursor.fetchall(), columns=['Symbol', 'Price'])
        except Exception as e:
            print(e)
            return self.sql_get_all_prices()

    def sql_get_price(self, symbol: str):
        """
        Gets the most recent price of one specific stock
        :param symbol: stock name
        :return: the most recent price of the stock requested as well as the name of the stock in a dataframe
        """
        postgresql_select_query = "select price from Prices where ticker = %s"
        self.cursor.execute(postgresql_select_query, (symbol,))
        return float(self.cursor.fetchone()[0])

    def sql_load_pairs(self, pairs: pd.DataFrame):
        """
        Loads the save database with if a pair is active and how many shares of a stock is bought.
        :param pairs: Dataframe with data from pairs strategy
        :return: None
        """

        pairs['active'] = False
        pairs['long'] = None
        pairs['shares_stock1'] = 0.000
        pairs['shares_stock2'] = 0.000

        try:
            pairs.to_sql('save', con=self.engine, if_exists='fail', index=False)
            with self.engine.connect() as con:
                con.execute('ALTER TABLE Save ADD PRIMARY KEY (t1,t2);')
        except Exception as e:
            print(e)

    def sql_update_pairs(self, pairs: pd.DataFrame):
        """
        Updates the save database with new data about all stock that pairs trading has active
        :param pairs: Dataframe with data from pairs strategy
        :return: None
        """
        try:
            pairs.to_sql('save', con=self.engine, if_exists='replace', index=False)
            with self.engine.connect() as con:
                con.execute('ALTER TABLE Save ADD PRIMARY KEY (t1,t2);')
        except Exception as e:
            print(e)

    def sql_get_saved(self):
        """
        Gets backup of all of the pairs, if they are active, a numeric value and how many of each stock is bought in
         pairs trading restore the program in case it is needed
        :return: dataframe values needed to restore the functionality of paris trading
        """
        try:
            postgresql_select_query = "select * from Save"
            self.cursor.execute(postgresql_select_query)
            return pd.DataFrame.from_records(self.cursor.fetchall(),
                                             columns=['t1', 't2', 'active', 'long', 'shares_stock1', 'shares_stock2'])
        except Exception as e:
            print(e)
            return self.sql_get_saved()
