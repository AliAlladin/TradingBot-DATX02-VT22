import psycopg2

DB_HOST = "abul.db.elephantsql.com"
DB_NAME = "rqagkzhe"
DB_USER = "rqagkzhe"
DB_PASSWORD = "YqrPGccyhM2WdWT0tvS99jm-50JQhHtU"
DB_PORT = "5432"

try:
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Database connected Successfully")

except:
    print("Database not Connected")
