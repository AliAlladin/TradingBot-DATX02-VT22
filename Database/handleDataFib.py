import pandas as pd
import psycopg2
from sqlalchemy import create_engine


class DatabaseHandler:
    def __init__(self):
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
        query = query.replace('a1', "\'" + stockTicker + "\'")
        query = query.replace('a2', str(price))
        query = query.replace('a3', str(volume))
        self.cursor.execute(query)
        self.conn.commit()

    def sqlBuy(self, stockTicker: str, price: float, volume: float):
        query = "INSERT INTO BuyF VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    # inserts into sell
    def sqlSell(self, stockTicker: str, price: float, volume: float):
        query = "INSERT INTO SellF VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    # inserts into blank
    def sqlShort(self, stockTicker: str, price: float, volume: float):
        query = "INSERT INTO ShortF VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
        self.insertAndCommitQuery(stockTicker, price, volume, query)

    # inserts into pairs
    def sqlPairs(self, stockTicker1: str, stockTicker2: str, standardDiv: float):
        query = "INSERT INTO SellF VALUES (a1 ,a2, a3)"
        query = query.replace('a1', "\'" + stockTicker1 + "\'")
        query = query.replace('a2', "\'" + stockTicker2 + "\'")
        query = query.replace('a3', str(standardDiv))
        self.cursor.execute(query)
        self.conn.commit()

    def sqlUpdatePrice(self, stockTicker: str, price: float):
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
        try:
            postgreSQL_select_Query = "select * from PricesF"
            self.cursor.execute(postgreSQL_select_Query)
            return pd.DataFrame.from_records(self.cursor.fetchall(), columns=['Symbol', 'Price'])
        except Exception as e:
            print(e)
            return self.sqlGetAllPrices()

    def sqlGetPrice(self, symbol: str):
        postgreSQL_select_Query = "select price from PricesF where ticker = %s"
        self.cursor.execute(postgreSQL_select_Query, (symbol,))
        return float(self.cursor.fetchone()[0])

    def sqlLoadFib(self, ratio: pd.DataFrame, tickers: pd.DataFrame):

        for index, row in tickers.iterrows():
            ratio[row['ticker']] = False

        ratio.set_index(0, inplace=True)

        try:
            ratio.to_sql('savef', con=self.engine, if_exists='fail', index=False)
        except Exception as e:
            print(e)

    def sqlUpdateFib(self, pairs: pd.DataFrame):
        try:
            pairs.to_sql('savef', con=self.engine, if_exists='replace', index=False)

        except Exception as e:
            print(e)

    def sqlGetSaved(self):
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
