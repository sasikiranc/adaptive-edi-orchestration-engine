from fastapi import APIRouter, Depends
from uuid import uuid4
from app.models.routingrules import RuleCreate, RuleResponse
from app.core.security import validate_admin_token, validate_token
from sqlalchemy.orm import Session
from app.persistence.db import get_db
from sqlalchemy import text

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("/", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db),user=Depends(validate_admin_token)):
    result = db.execute(text("SELECT * FROM routing_rules WHERE active = TRUE"))
    rows = result.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "source_system": row[1],
            "receiver_system": row[2],
            "message_type": row[3],
            "partner_id": row[4],
            "version": row[5],
            "direction": row[6],
            "target_endpoint": row[7],
            "mapping_id": row[8],
            "active": row[9],
        })
    return results

@router.post("/", response_model=RuleResponse)
def create_rule(rule: RuleCreate,
                db: Session = Depends(get_db),
                user=Depends(validate_admin_token)):

    rule_id = str(uuid4())

    db.execute(
        text("""
            INSERT INTO routing_rules
            (id, source_system, receiver_system, message_type, partner_id, version, direction, target_endpoint, mapping_id, active)
            VALUES (:id,:source_system,:receiver_system,:message_type,:partner_id,:version,:direction,:target_endpoint,:mapping_id,:active)
        """),
        {
            "id": rule_id,
            "source_system": rule.source_system,
            "receiver_system": rule.receiver_system,
            "message_type": rule.message_type.upper(),
            "partner_id": rule.partner_id,
            "version": rule.version,
            "direction": rule.direction,
            "target_endpoint": rule.target_endpoint,
            "mapping_id": rule.mapping_id,
            "active": rule.active
        }
    )
    db.commit()
    return {
        "id": rule_id,
        **rule.dict(),
        "active": True
    }

@router.delete("/{rule_id}")
def deactivate_rule(rule_id: str,
                    db: Session = Depends(get_db),
                    user=Depends(validate_admin_token)):

    db.execute(
        text("""
            UPDATE routing_rules
            SET active = FALSE
            WHERE id = :rule_id
        """),
        {"rule_id": rule_id}
    )

    db.commit()
    return {"status": "deactivated"}