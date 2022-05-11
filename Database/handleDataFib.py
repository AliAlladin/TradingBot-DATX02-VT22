import numpy as np

import pandas as pd
import psycopg2
from sqlalchemy import create_engine


class DatabaseHandler:
    """
    This class sets up a connection to a postgres server on post 5432 and creates all tables, views and queries for
    a database that saves information for the fibonacci strategy.
    """

    def __init__(self):
        """
        Constructor for the class that sets up a connection to the database server and sets up required tables
        """

        self.conn = psycopg2.connect(
            host="localhost",
            database="tradingBot2",
            user="postgres",
            password="postgres",
            port="5432"
        )
        self.engine = create_engine('postgresql://postgres:postgres@localhost:5432/tradingBot2')

        self.cursor = self.conn.cursor()

        print("Database Connected Successfully")

        cursor = self.conn.cursor()

        # drop
        # sql = open('../Database/drop.sql', 'r')
        # cursor.execute(sql.read())
        # self.conn.commit()
        # print("drop table")

        # Tables
        sql = open('../Database/tableFib.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("Table created")

    def insertAndCommitQuery(self, stockTicker: str, price: float, volume: float, query: str):
        """
        Inserts values into a query and executes to so that it is saved on the server
        :param stockTicker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :param query: the query that is going to be committed to the server.
        :return: None
        """
        query = query.replace('a1', "\'" + stockTicker + "\'")
        query = query.replace('a2', str(price))
        query = query.replace('a3', str(volume))
        self.cursor.execute(query)
        self.conn.commit()

    def sqlBuy(self, stockTicker: str, price: float, volume: float):
        """
        Saves information to the server if the system buys a stock
        :param stockTicker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :return: None
        """
        query = "INSERT INTO BuyF VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    def sqlSell(self, stockTicker: str, price: float, volume: float):
        """
        Saves information to the server if the system sells a stock
        :param stockTicker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :return: None
        """
        query = "INSERT INTO SellF VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    def sqlShort(self, stockTicker: str, price: float, volume: float):
        """
        Saves information to the server if the system shorts a stock
        :param stockTicker: string with stock name
        :param price: float with stock price
        :param volume: float with how much volume the stock has
        :return: None
        """
        query = "INSERT INTO ShortF VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    def sqlUpdatePrice(self, stockTicker: str, price: float):
        """
        Creates a table PriceF if it doesnt exist that saves the prices of all the stocks that are needed in fibonacci
        :param stockTicker: name of a stock
        :param price: price of a stock
        :return: None
        """
        query = "INSERT INTO PricesF (ticker, price) VALUES(a2, a1) ON CONFLICT (ticker) DO UPDATE SET price = a1 " \
                "WHERE PricesF.ticker = a2 "
        query = query.replace('a1', str(price))
        query = query.replace('a2', "\'" + str(stockTicker) + "\'")
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(stockTicker)
            print(e)

    def sqlGetAllPrices(self):
        """
        Returns all the values in PriceF which include stock names and the most recent price of that stock
        :return: Dataframe with all prices of all stocks in the database
        """
        try:
            postgreSQL_select_Query = "select * from PricesF"
            self.cursor.execute(postgreSQL_select_Query)
            return pd.DataFrame.from_records(self.cursor.fetchall(), columns=['Symbol', 'Price'])
        except Exception as e:
            print(e)
            return self.sqlGetAllPrices()

    def sqlGetPrice(self, symbol: str):
        """
        Gets the most recent price of one specific stock
        :param symbol: stock name
        :return: the most recent price of the stock requested as well as the name of the stock in a dataframe
        """
        postgreSQL_select_Query = "select price from PricesF where ticker = %s"
        self.cursor.execute(postgreSQL_select_Query, (symbol,))
        return float(self.cursor.fetchone()[0])

    def sqlLoadFib(self, ratio: pd.DataFrame, tickers: pd.DataFrame):
        """
        Reloads the system with all the information needed for fibonacci if the system crashes or restarts.
        :param ratio: a dataframe with all the ratios required
        :param tickers: a dataframe with all the tickers saved in the database
        :return: None
        """
        for index, row in tickers.iterrows():
            ratio[row['ticker']] = False

        ratio.set_index(0, inplace=True)

        try:
            ratio.to_sql('savef', con=self.engine, if_exists='fail', index=False)
        except Exception as e:
            print(e)

    def sqlLoadInvestments(self, tickers: pd.DataFrame):
        """
        Saves the volume and ticker name of a bought stock. If the table doesnt exist it is created
        :param tickers: stock name
        :return: None
        """
        tickers2 = tickers.copy()
        tickers2.rename(columns={'ticker': 'symbol'}, inplace=True)
        tickers2['volume'] = 0
        tickers2['volume'].astype(np.float64)

        try:
            tickers2.to_sql('investmentsf', con=self.engine, if_exists='fail', index=False)
            with self.engine.connect() as con:
                con.execute('ALTER TABLE investmentsf ADD PRIMARY KEY (symbol);')
        except Exception as e:
            print(e)

    def sqlUpdateInvestments(self, investments: pd.DataFrame):
        """
        Updates the values in investmentsf
        :param investments: dataframe with new investments
        :return: None
        """
        try:
            investments.to_sql('investmentsf', con=self.engine, if_exists='replace', index=False)
            with self.engine.connect() as con:
                con.execute('ALTER TABLE investmentsf ADD PRIMARY KEY (symbol);')
        except Exception as e:
            print(e)

    def sqlGetInvestments(self):
        """
        Get the volume and stock that have been invested in
        :return: dataframe with symbol and volume from investmentF table
        """
        try:
            postgreSQL_select_Query = "select * from investmentsf"
            self.cursor.execute(postgreSQL_select_Query)
            return pd.DataFrame.from_records(self.cursor.fetchall(), columns=['symbol', 'volume'])
        except Exception as e:
            print(e)

    def sqlUpdateFib(self, stock: pd.DataFrame):
        """
        Updates all values in save file to have a save if program crashes or is closed
        :param stock: all stocks that need to be saved
        :return: None
        """
        try:
            stock.to_sql('savef', con=self.engine, if_exists='replace', index=False)

        except Exception as e:
            print(e)

    def sqlGetSaved(self):
        """
        Gets backup of all of the investments in fibonacci to restore the program in case it is needed
        :return: dataframe with all stocks and the levels they are invested at
        """
        try:
            postgreSQL_select_Query = "select * from savef"
            self.cursor.execute(postgreSQL_select_Query)
            column_names = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame.from_records(self.cursor.fetchall())
            df.columns = column_names
            df['levels'] = [0.382, 0.500, 0.618]
            df.set_index('levels', inplace=True)
            return df

        except Exception as e:
            print(e)
            return self.sqlGetSaved()
