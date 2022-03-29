import psycopg2

# setup databas
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

class DatabaseHandler:
    def __init__(self):
        self.conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        self.cursor = self.conn.cursor()

        print("Database Connected Successfully")

    def insertAndCommitQuery(stockTicker: str, price: float, query: str):
        query = query.replace('a1', "\'" + stockTicker + "\'")
        query = query.replace('a2', str(price))
        cursor.execute(query)
        conn.commit()

    def sqlBuy(self, stockTicker: str, price: float):
        query = "INSERT INTO Buy VALUES (DEFAULT,a1,current_timestamp ,a2)"
        self.insertAndCommitQuery(stockTicker, price, query)

    # inserts into sell
    def sqlSell(self, stockTicker: str, price: float):
        query = "INSERT INTO Sell VALUES (DEFAULT,a1,current_timestamp ,a2)"
        self.insertAndCommitQuery(stockTicker, price, query)

    # inserts into blank
    def sqlBlank(self, stockTicker: str, price: float):
        query = "INSERT INTO Blank VALUES (DEFAULT,a1,current_timestamp ,a2)"
        self.insertAndCommitQuery(stockTicker, price, query)

    # inserts into pairs
    def sqlPairs(self, stockTicker1: str, stockTicker2: str, standardDiv: float):
        query = "INSERT INTO Sell VALUES (a1 ,a2, a3)"
        query = query.replace('a1', "\'" + stockTicker1 + "\'")
        query = query.replace('a2', "\'" + stockTicker2 + "\'")
        query = query.replace('a3', str(standardDiv))
        cursor.execute(query)
        self.conn.commit()

    def sqlUpdatePrice(self, stockTicker: str, price: float):
        query = "UPDATE Prices SET price = a1 WHERE ticker = a2"
        query = query.replace('a1', str(price))
        query = query.replace('a2', "\'" + stockTicker + "\'")
        cursor.execute(query)
        self.conn.commit()

    def sqlGetAllPrice(self):
        postgreSQL_select_Query = "select * from Prices"
        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from prices table using cursor.fetchall")
        return cursor.fetchall()
