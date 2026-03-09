from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime


def register_historical_route(
    db: Session,
    canonical,
    endpoint,
    tpm,
    confidence,
    decision_type,
    request_id
):

    db.execute(
        text("""
            INSERT INTO historical_routes
            (message_type, source_system, receiver_system, msg_format, version,
             partner_id, control_number, direction, target_endpoint,
             tpm, confidence, decision_type, request_id)
            VALUES
            (:message_type, :source_system, :receiver_system, :msg_format, :version,
             :partner_id, :control_number, :direction, :target_endpoint,
             :tpm, :confidence, :decision_type, :request_id)
        """),
        {
            "message_type": canonical.message_type,
            "source_system": canonical.source_system,
            "receiver_system": canonical.receiver_system,
            "msg_format": canonical.format,
            "version": canonical.version,
            "partner_id": canonical.partner_id,
            "control_number": canonical.control_number,
            "direction": canonical.direction,
            "target_endpoint": endpoint,
            "tpm": tpm,
            "confidence": confidence,
            "decision_type": decision_type,
            "request_id": request_id
        }
    )

    db.execute(
        text("""
            INSERT INTO routing_audit
            (request_id, message_type, partner_id, direction, endpoint,
             mapping_id, decision_type, confidence, version, timestamp)
            VALUES
            (:request_id, :message_type, :partner_id, :direction, :endpoint,
             :mapping_id, :decision_type, :confidence, :version, :timestamp)
        """),
        {
            "request_id": request_id,
            "message_type": canonical.message_type,
            "partner_id": canonical.partner_id,
            "direction": canonical.direction,
            "endpoint": endpoint,
            "mapping_id": tpm,
            "decision_type": decision_type,
            "confidence": confidence,
            "version": canonical.version,
            "timestamp": datetime.utcnow()
        }
    )

    db.commit()