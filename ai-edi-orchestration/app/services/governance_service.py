import uuid
from datetime import datetime
from sqlalchemy import text


def manual_override(db, control_number: str, target_endpoint: str, tpm_mapping_id: str):

    # 1️⃣ Fetch existing historical record
    result = db.execute(
        text("""
            SELECT message_type, msg_format, source_system,
                   receiver_system, partner_id, direction, version
            FROM historical_routes
            WHERE control_number = :control_number
        """),
        {"control_number": control_number}
    )

    row = result.fetchone()

    if not row:
        raise ValueError("Control number not found in historical_routes")

    message_type, msg_format, source_system, receiver_system, partner_id, direction, version = row

    # 2️⃣ Update historical_routes
    db.execute(
        text("""
            UPDATE historical_routes
            SET target_endpoint = :target_endpoint,
                tpm = :tpm,
                decision_type = 'MANUAL_OVERRIDE',
                confidence = :confidence
            WHERE control_number = :control_number
        """),
        {
            "target_endpoint": target_endpoint,
            "tpm": tpm_mapping_id,
            "confidence": 1.0,
            "control_number": control_number
        }
    )

    # 3️⃣ Insert into routing_audit
    request_id = str(uuid.uuid4())

    db.execute(
        text("""
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
            VALUES (
                :message_type,
                :partner_id,
                :version,
                :direction,
                :decision_type,
                :confidence,
                :endpoint,
                :mapping_id,
                :request_id,
                :timestamp
            )
        """),
        {
            "message_type": message_type,
            "partner_id": partner_id,
            "version": version,
            "direction": direction,
            "decision_type": "MANUAL_OVERRIDE",
            "confidence": 1.0,
            "endpoint": target_endpoint,
            "mapping_id": tpm_mapping_id,
            "request_id": request_id,
            "timestamp": datetime.utcnow()
        }
    )

    db.commit()

    return {"status": "OVERRIDE_SUCCESS"}