import psycopg2
import datetime
import time

from psycopg2.sql import DEFAULT

DB_HOST = "abul.db.elephantsql.com"
DB_NAME = "rqagkzhe"
DB_USER = "rqagkzhe"
DB_PASSWORD = "YqrPGccyhM2WdWT0tvS99jm-50JQhHtU"
DB_PORT = "5432"

conn = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

print("Database Connected Successfully")

cursor = conn.cursor()
sql = open('tables.sql', 'r')
cursor.execute(sql.read())
conn.commit()

print("table created")

sql = open('views.sql', 'r')
cursor.execute(sql.read())
conn.commit()

print("views created")

sql = open('triggers.sql', 'r')
cursor.execute(sql.read())
conn.commit()

print("triggers created")


##sql = open('inserts.sql', 'r')
##cursor.execute(sql.read())
##conn.commit()
##print("inserts created")


def sqlBuy(stockTicker: str, price: float):
    query = "INSERT INTO Buy VALUES (DEFAULT,a1,current_timestamp ,a2,a3)"
    query = query.replace('a1', "\'" + stockTicker + "\'")
    query = query.replace('a2', str(price))
    query = query.replace('a3', "\'" + 'Active ' + "\'")
    cursor.execute(query)
    conn.commit()


def sqlSell(stockTicker: str, price: float):
    query = "INSERT INTO Sell VALUES (DEFAULT,a1,current_timestamp ,a2)"
    query = query.replace('a1', "\'" + stockTicker + "\'")
    query = query.replace('a2', str(price))
    cursor.execute(query)
    conn.commit()


def sqlPairs(stockTicker1: str, stockTicker2: str, standardDiv: float):
    query = "INSERT INTO Sell VALUES (a1 ,a2, a3)"
    query = query.replace('a1', "\'" + stockTicker1 + "\'")
    query = query.replace('a2', "\'" + stockTicker2 + "\'")
    query = query.replace('a3', str(standardDiv))
    cursor.execute(query)
    conn.commit()
