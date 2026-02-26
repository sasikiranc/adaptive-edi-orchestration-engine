from app.persistence.db import get_db_connection
from datetime import datetime


def register_historical_route(canonical, endpoint, tpm, confidence, decision_type, request_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO historical_routes
        (message_type, source_system, receiver_system, msg_format, version, partner_id, control_number, direction, target_endpoint, tpm, confidence, decision_type, request_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
     """, 
        (
            canonical.message_type,
            canonical.source_system,
            canonical.receiver_system,
            canonical.format,
            canonical.version,
            canonical.partner_id,
            canonical.control_number,
            canonical.direction,
            endpoint,
            tpm,
            confidence,
            decision_type,
            request_id
        )
    )

    cur.execute("""
        INSERT INTO routing_audit (
            request_id,
            message_type,
            partner_id,
            direction,
            endpoint,
            mapping_id,
            decision_type,
            confidence,
            version,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        request_id,
        canonical.message_type,
        canonical.partner_id,
        canonical.direction,
        endpoint,
        tpm,
        "MANUAL_OVERRIDE",
        1.0,
        canonical.version,
        datetime.utcnow()
    ))

    conn.commit()
    cur.close()
    conn.close()