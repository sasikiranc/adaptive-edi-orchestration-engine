import psycopg2
import os
from app.persistence.db import get_db_connection

def main():
    
    conn = get_db_connection()

    #query_sql = "SELECT json_agg(t) FROM (select * from decision_weights) t;"
    #query_sql = "SELECT json_agg(t) FROM (SELECT * FROM confidence_thresholds) t;"
    query_sql = "SELECT json_agg(t) FROM (select * from partner_identity_map) t;"

    cur = conn.cursor()
    cur.execute(query_sql)
    version = cur.fetchall()
    print(version)

    conn.commit()
    cur.close()
    conn.close()




if __name__ == "__main__":
    main()