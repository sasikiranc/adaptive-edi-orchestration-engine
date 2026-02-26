from app.persistence.db import get_db_connection
import uuid
from datetime import datetime


def manual_override(control_number: str, target_endpoint: str, tpm_mapping_id: str):

    conn = get_db_connection()
    cur = conn.cursor()

    # 1️⃣ Fetch existing historical record
    cur.execute("""
        SELECT message_type, msg_format, source_system,
               receiver_system, partner_id, direction, version
        FROM historical_routes
        WHERE control_number = %s
    """, (control_number,))

    row = cur.fetchone()

    if not row:
        raise ValueError("Control number not found in historical_routes")

    message_type, msg_format, source_system, receiver_system, partner_id, direction, version = row

    # 2️⃣ Update historical_routes
    cur.execute("""
        UPDATE historical_routes
        SET target_endpoint = %s,
            tpm = %s,
            decision_type = 'MANUAL_OVERRIDE',
            confidence = %s
        WHERE control_number = %s
    """, (target_endpoint, tpm_mapping_id, 1.0, control_number))

    # 3️⃣ Insert into routing_audit
    request_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO routing_audit (
            message_type,
            partner_id,
            version,
            direction,
            decision_type,
            confidence,
            endpoint,
            mapping_id,
            request_id,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        message_type,
        partner_id,
        version,
        direction,
        "MANUAL_OVERRIDE",
        1.0,
        target_endpoint,
        tpm_mapping_id,
        request_id,
        datetime.utcnow()
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"status": "OVERRIDE_SUCCESS"}