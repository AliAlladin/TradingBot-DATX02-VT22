import psycopg2
import pandas as pd


class DatabaseHandler:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="tradingBot",
            user="postgres",
            password="postgres",
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

        
        # insert
        sql = open('../Database/inserts.sql', 'r')
        cursor.execute(sql.read())
        self.conn.commit()
        print("insert created")


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
        self.cursor.execute(query)
        self.conn.commit()

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
        self.cursor.execute(postgreSQL_select_Query, (symbol, ))
        return float(self.cursor.fetchone()[0])
