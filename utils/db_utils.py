import psycopg2

def connect_db():
    return psycopg2.connect(
        host="localhost",
        dbname="db_articles",
        user="postgres",
        password="0000"
    )
