import json
from typing import List, Optional
from app.models.canonical import CanonicalMessage
from app.routing.similarity_engine import embedding_route_suggestion, fetch_historical_routes
import csv
from app.core.config import DEFAULT_THRESHOLD
from fastapi import Request
import logging
from app.persistence.repositories.repository import register_historical_route
from app.models.routingrules import RuleCreate
from app.persistence.db import get_db_connection
from app.services.config_cache import CONFIG_CACHE

class RuleEngine:

    def __init__(self):
        self.load_rules()


    def load_rules(self):
        
        self.rules = load_rules_from_db()

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        logger.info(
            "Rule Engine Loaded decision",
            extra={
                "No of rules loaded": len(self.rules)
            })

    
    def find_routing_rule(self, message: CanonicalMessage):
        for rule in self.rules:
            if not rule.active:
                continue

            if (
                rule.message_type == message.message_type and
                rule.source_system == message.source_system and
                rule.receiver_system == message.receiver_system and
                (rule.version == message.version or rule.version == "")
            ):
                return rule

        return None

    def route_message(self, canonical_message: CanonicalMessage):
        rule = self.find_routing_rule(canonical_message)

        if not rule:
            return {
                "status": "ANOMALY",
                "reason": "No matching routing rule found",
                "control_number": canonical_message.control_number
            }

        return {
            "status": "ROUTED",
            "control_number": canonical_message.control_number,
            "endpoint": rule.endpoint,
            "tpm_mapping_id": rule.tpm_mapping_id
        }

    def route_with_ai(self, canonical_message: CanonicalMessage, request_id):

        # 1️⃣ Deterministic rule
        rule = self.find_routing_rule(canonical_message)
        request_id = request_id

        if rule:
            # After rule-based routing success
            register_historical_route(canonical_message, rule.target_endpoint, rule.mapping_id,"1.0","ROUTED_RULE",request_id)
            logger_request(canonical_message, "ROUTED_RULE", "1.0", request_id, rule.target_endpoint, rule.mapping_id)
            return {
                "status": "ROUTED_RULE",
                "endpoint": rule.target_endpoint,
                "tpm_mapping": rule.mapping_id
            }

        # 2️⃣ Embedding fallback
        ai_result = embedding_route_suggestion(canonical_message)

        CONFIDENCE_THRESHOLDS = CONFIG_CACHE.get("CONFIDENCE_THRESHOLDS", [])

        threshold = CONFIDENCE_THRESHOLDS.get(
            canonical_message.message_type,
            DEFAULT_THRESHOLD
        )

        if ai_result and ai_result["confidence"] >= threshold:
            register_historical_route(canonical_message, ai_result["endpoint"], ai_result["tpm"],ai_result["confidence"],ai_result["status"],request_id)
            logger_request(canonical_message,"ROUTED_AI", round(ai_result["confidence"],2), request_id, ai_result["endpoint"], ai_result["tpm"])
            return {
                "status": "ROUTED_AI",
                "endpoint": ai_result["endpoint"],
                "tpm_mapping": ai_result["tpm"],
                "confidence": str(round(ai_result["confidence"],2))
            }

        # 3️⃣ Park
        status = "PARKED_MANUAL_REVIEW"
        reason = ai_result["reason"] if ai_result else "NO_HISTORICAL_MATCH"
        register_historical_route(canonical_message,"","",0.0,ai_result["status"],request_id)
        logger_request(canonical_message,status,round(ai_result["confidence"],2),request_id,"","")
        return {
            "status": status,
            "confidence": round(ai_result["confidence"],2) if ai_result else 0.0,
            "reason": reason
        }

def logger_request(canonical_message, decision_type, confidence, request_id, endpoint, tpm):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(
        "Routing decision",
        extra={
            "request_id": request_id,
            "message_type": canonical_message.message_type,
            "decision_type": decision_type,
            "confidence": confidence
        }
    )

def load_rules_from_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""SELECT * FROM routing_rules where active = TRUE""")
    rows = cur.fetchall()

    active_rules = []

    for row in rows:
        rulecreate = RuleCreate(
            source_system=row[1],
            receiver_system=row[2],
            message_type=row[3],
            partner_id=row[4],
            version=row[5],
            direction=row[6],
            target_endpoint=row[7],
            mapping_id=row[8],
            active=row[9]
        )

        active_rules.append(rulecreate)
    

    cur.close()
    conn.close()
    return active_rules