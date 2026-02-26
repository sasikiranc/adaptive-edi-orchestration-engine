import psycopg2
import os
from app.persistence.db import get_db_connection
import uuid

def main():
    
    conn = get_db_connection()

    #query_sql = 'create table historical_routes (message_type VARCHAR(255), source_system VARCHAR(255), receiver_system VARCHAR(255), msg_format VARCHAR(255), version VARCHAR(255), partner_id VARCHAR(255), control_number VARCHAR(255), direction VARCHAR(255), target_endpoint VARCHAR(255), tpm VARCHAR(255), confidence VARCHAR(255), decision_type VARCHAR(255), request_id VARCHAR(255))'

    #query_sql = 'create table routing_audit (request_id VARCHAR(255), message_type VARCHAR(255), partner_id VARCHAR(255), version VARCHAR(255), direction VARCHAR(255), decision_type VARCHAR(255), confidence VARCHAR(255), endpoint VARCHAR(255), mapping_id VARCHAR(255), timestamp VARCHAR(255))'

    #query_sql = 'CREATE TABLE routing_rules (id UUID PRIMARY KEY, source_system VARCHAR(50), receiver_system VARCHAR(50), message_type VARCHAR(50) NOT NULL, partner_id VARCHAR(100), version VARCHAR(20), direction VARCHAR(20), target_endpoint VARCHAR(255) NOT NULL, mapping_id VARCHAR(255) NOT NULL, active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'

    '''query_list = ['CREATE TABLE message_types (code VARCHAR PRIMARY KEY, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE systems (code VARCHAR PRIMARY KEY, system_type VARCHAR, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE directions (code VARCHAR PRIMARY KEY, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE versions (code VARCHAR PRIMARY KEY, active BOOLEAN DEFAULT TRUE);',
                  'CREATE TABLE similarity_weights (feature_name VARCHAR PRIMARY KEY, weight FLOAT);',
                  'CREATE TABLE confidence_thresholds (code VARCHAR PRIMARY KEY, confidence_threshold FLOAT);',
                  'CREATE TABLE decision_weights (decision_type VARCHAR PRIMARY KEY, weight FLOAT);']
'''

    cur = conn.cursor()
    #cur.execute(query_sql)

    '''for i in query_list:
        cur.execute(i)'''

    id = uuid.uuid4()
    '''cur.execute("""
         INSERT INTO routing_rules
         (id, source_system, receiver_system, message_type, partner_id, version, direction, target_endpoint, mapping_id, active)
         VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)
      """, 
         (
		    str(id),"CUSTOMER03","S4CLNT100","ORDERS","CUSTOMER03","","OUTBOUND","CPI_EDI_TO_IDOC","TPM_ORDERS_850",True
         )
 )'''

    cur.execute("""
         INSERT INTO similarity_weights
         (feature_name, weight)
         VALUES (%s,%s)
      """, 
         (
		    "receiver_system",1.3
         )
    )
    
    conn.commit()
    cur.close()
    conn.close()




if __name__ == "__main__":
    main()