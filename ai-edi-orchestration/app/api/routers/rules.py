from fastapi import APIRouter, Depends
from uuid import uuid4
from app.models.routingrules import RuleCreate, RuleResponse
from app.core.security import validate_admin_token, validate_token
from app.persistence.db import get_db_connection

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("/", response_model=list[RuleResponse])
def get_rules(user=Depends(validate_admin_token)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM routing_rules WHERE active = TRUE")
    rows = cur.fetchall()

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
                user=Depends(validate_admin_token)):

    conn = get_db_connection()
    cur = conn.cursor()

    rule_id = str(uuid4())

    cur.execute("""
        INSERT INTO routing_rules
        (id, source_system, receiver_system, message_type, partner_id, version, direction, target_endpoint, mapping_id, active)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
    """, (
        rule_id,
        rule.source_system,
        rule.receiver_system,
        rule.message_type.upper(),
        rule.partner_id,
        rule.version,
        rule.direction,
        rule.target_endpoint,
        rule.mapping_id,
        rule.active
    ))

    conn.commit()

    return {
        "id": rule_id,
        **rule.dict(),
        "active": True
    }

@router.delete("/{rule_id}")
def deactivate_rule(rule_id: str,
                    user=Depends(validate_admin_token)):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE routing_rules
        SET active = FALSE
        WHERE id = %s
    """, (rule_id,))

    conn.commit()

    return {"status": "deactivated"}