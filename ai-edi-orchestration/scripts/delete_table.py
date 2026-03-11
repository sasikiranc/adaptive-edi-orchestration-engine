import psycopg2
import os
from app.persistence.db import get_db_connection

def main():
    
    conn = get_db_connection()

    query_sql = 'truncate table routing_rules'

    cur = conn.cursor()
    cur.execute(query_sql)

    conn.commit()
    cur.close()
    conn.close()




if __name__ == "__main__":
    main()