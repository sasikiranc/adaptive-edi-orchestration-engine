import os
import psycopg2
from psycopg2 import pool

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set")

db_pool = pool.SimpleConnectionPool(
    1,
    10,
    dsn=DATABASE_URL,
    sslmode="require"
)

def get_db_connection():
    return db_pool.getconn()

def release_connection(conn):
    db_pool.putconn(conn)