import pandas as pd
import psycopg2
from sqlalchemy import create_engine


class DatabaseHandler:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="tradingBot",
            user="postgres",
            password="asdasd123",
            port="5432"
        )

        self.cursor = self.conn.cursor()

        print("Database Connected Successfully")

        cursor = self.conn.cursor()

        # drop
        sql = open('../Database/drop.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("drop table")

        # Tables
        sql = open('../Database/tables.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("Table created")

        # Views
        sql = open('../Database/views.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("views created")

    def insertAndCommitQuery(self, stockTicker: str, price: float, volume: float, query: str):
        query = query.replace('a1', "\'" + stockTicker + "\'")
        query = query.replace('a2', str(price))
        query = query.replace('a3', str(volume))
        self.cursor.execute(query)
        self.conn.commit()

    def sqlBuy(self, stockTicker: str, price: float, volume: float):
        query = "INSERT INTO Buy VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    # inserts into sell
    def sqlSell(self, stockTicker: str, price: float, volume: float):
        query = "INSERT INTO Sell VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    # inserts into blank
    def sqlShort(self, stockTicker: str, price: float, volume: float):
        query = "INSERT INTO Short VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    # inserts into pairs
    def sqlPairs(self, stockTicker1: str, stockTicker2: str, standardDiv: float):
        query = "INSERT INTO Sell VALUES (a1 ,a2, a3)"
        query = query.replace('a1', "\'" + stockTicker1 + "\'")
        query = query.replace('a2', "\'" + stockTicker2 + "\'")
        query = query.replace('a3', str(standardDiv))
        self.cursor.execute(query)
        self.conn.commit()

    def sqlUpdatePrice(self, stockTicker: str, price: float):
        query = "INSERT INTO Prices (ticker, price) VALUES(a2, a1) ON CONFLICT (ticker) DO UPDATE SET price = a1 " \
                "WHERE Prices.ticker = a2 "
        query = query.replace('a1', str(price))
        query = query.replace('a2', "\'" + str(stockTicker) + "\'")
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(stockTicker)
            print(e)

    def sqlGetAllPrices(self):
        try:
            postgreSQL_select_Query = "select * from Prices"
            self.cursor.execute(postgreSQL_select_Query)
            return pd.DataFrame.from_records(self.cursor.fetchall(), columns=['Symbol', 'Price'])
        except Exception as e:
            print(e)
            return self.sqlGetAllPrices()

    def sqlGetPrice(self, symbol: str):
        postgreSQL_select_Query = "select price from Prices where ticker = %s"
        self.cursor.execute(postgreSQL_select_Query, (symbol,))
        return float(self.cursor.fetchone()[0])

    def sqlLoadPairs(self, pairs: pd.DataFrame):
        engine = create_engine('postgresql://postgres:asdasd123@localhost:5432/tradingBot')

        print(pairs)
        pairs['active'] = False
        pairs['long'] = None
        pairs['shares_stock1'] = 0.000
        pairs['shares_stock2'] = 0.000

        try:
            pairs.to_sql('save', con=engine, if_exists='fail', index=False)
        except Exception as e:
            print(e)

        with engine.connect() as con:
            con.execute('ALTER TABLE Save ADD PRIMARY KEY (t1,t2);')

    def sqlSave(self, ticker1: str, ticker2: str, active: bool, whichBuy: bool, amount1: float, amount2: float):
        query = "UPDATE save SET active=a1, long=a2, shares_stock1=a3, shares_stock2=a4 WHERE t1=a5 AND t2=a6"
        query = query.replace('a1', str(active))
        query = query.replace('a2', str(whichBuy))
        query = query.replace('a3', str(amount1))
        query = query.replace('a4', str(amount2))
        query = query.replace('a5', "\'" + ticker1 + "\'")
        query = query.replace('a6', "\'" + ticker2 + "\'")
        print(query)
        self.cursor.execute(query)
        self.conn.commit()

    def sqlGetSaved(self):
        try:
            postgreSQL_select_Query = "select * from Save"
            self.cursor.execute(postgreSQL_select_Query)
            return pd.DataFrame.from_records(self.cursor.fetchall(),
                                             columns=['Ticker1', 'Ticker2', 'Active', 'WhichBuy', 'Amount1', 'Amount2'])
        except Exception as e:
            print(e)
            return self.sqlGetAllPrices()
