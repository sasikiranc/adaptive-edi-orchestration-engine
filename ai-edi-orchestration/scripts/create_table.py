import psycopg2
import os
from app.persistence.db import get_db_connection

def main():
    
    conn = get_db_connection()

    #query_sql = 'create table historical_routes (message_type VARCHAR(255), source_system VARCHAR(255), receiver_system VARCHAR(255), msg_format VARCHAR(255), version VARCHAR(255), partner_id VARCHAR(255), control_number VARCHAR(255), direction VARCHAR(255), target_endpoint VARCHAR(255), tpm VARCHAR(255), confidence VARCHAR(255), decision_type VARCHAR(255), request_id VARCHAR(255))'

    #query_sql = 'create table routing_audit (request_id VARCHAR(255), message_type VARCHAR(255), partner_id VARCHAR(255), version VARCHAR(255), direction VARCHAR(255), decision_type VARCHAR(255), confidence VARCHAR(255), endpoint VARCHAR(255), mapping_id VARCHAR(255), timestamp VARCHAR(255))'

    #query_sql = 'CREATE TABLE routing_rules (id UUID PRIMARY KEY, source_system VARCHAR(50), receiver_system VARCHAR(50), message_type VARCHAR(50) NOT NULL, partner_id VARCHAR(100), version VARCHAR(20), direction VARCHAR(20), target_endpoint VARCHAR(255) NOT NULL, mapping_id VARCHAR(255) NOT NULL, active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'

    query_list = ['CREATE TABLE message_types (code VARCHAR PRIMARY KEY, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE systems (code VARCHAR PRIMARY KEY, system_type VARCHAR, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE directions (code VARCHAR PRIMARY KEY, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE versions (code VARCHAR PRIMARY KEY, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE similarity_weights (feature_name VARCHAR PRIMARY KEY, weight FLOAT);',
                  'CREATE TABLE confidence_thresholds (code VARCHAR PRIMARY KEY, confidence_threshold FLOAT);',
                  'CREATE TABLE decision_weights (decision_type VARCHAR PRIMARY KEY, weight FLOAT);']

    cur = conn.cursor()
    #cur.execute(query_sql)

    '''for i in query_list:
        cur.execute(i)'''

    cur.execute(query_list[5])
    
    conn.commit()
    cur.close()
    conn.close()




if __name__ == "__main__":
    main()