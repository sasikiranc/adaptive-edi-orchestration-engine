import numpy as np
import json
from app.models.canonical import RoutingRule, CanonicalMessage, HistoricalRoute
from app.core.config import MIN_HISTORY_THRESHOLD
from app.services.config_cache import CONFIG_CACHE
from sqlalchemy import text

def build_feature_vector(message):

    vector = []

    MESSAGE_TYPES = CONFIG_CACHE.get("MESSAGE_TYPES", [])
    SYSTEMS = CONFIG_CACHE.get("SYSTEMS", [])
    VERSIONS = CONFIG_CACHE.get("VERSIONS", [])
    DIRECTIONS = CONFIG_CACHE.get("DIRECTIONS", [])
    WEIGHTS = CONFIG_CACHE.get("SIMILARITY_WEIGHTS", [])

    # Message Type
    for mt in MESSAGE_TYPES:
        value = 1 if message.message_type == mt else 0
        vector.append(value * WEIGHTS.get("message_type", 1.0))

    # Source System
    for sys in SYSTEMS:
        value = 1 if message.source_system == sys else 0
        vector.append(value * WEIGHTS.get("source_system", 1.0))

    # Receiver System
    for sys in SYSTEMS:
        value = 1 if message.receiver_system == sys else 0
        vector.append(value * WEIGHTS.get("receiver_system", 1.0))

    # Version
    for v in VERSIONS:
        value = 1 if message.version == v else 0
        vector.append(value * WEIGHTS.get("version", 1.0))

    # Direction
    for d in DIRECTIONS:
        value = 1 if message.direction == d else 0
        vector.append(value * WEIGHTS.get("direction", 1.0))

    return np.array(vector, dtype=float)


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (
        np.linalg.norm(v1) * np.linalg.norm(v2)
    )

def get_candidate_rules(canonical):

    key = (canonical.message_type, canonical.direction)

    return CONFIG_CACHE["CANDIDATE_INDEX"].get(key, [])

def embedding_route_suggestion(message, db):

    historical_routes = fetch_historical_routes(db,message.message_type,message.direction)

    filtered_routes = [
        row for row in historical_routes
        if row.canonical.message_type == message.message_type and 
            row.canonical.version == message.version and
            row.canonical.partner_id == message.partner_id and
            row.canonical.direction == message.direction
    ]

    if not filtered_routes or not is_bucket_mature(filtered_routes):
        return {
            "status": "PARKED_MANUAL_REVIEW",
            "confidence": 0.0,
            "reason": "NO_PARTNER_HISTORY"
        }

    incoming_vector = build_feature_vector(message)

    best_match = None
    best_score = -1

    DECISION_WEIGHTS = CONFIG_CACHE.get("DECISION_WEIGHTS", [])

    for row in filtered_routes:
        historical_vector = build_feature_vector(row.canonical)
        
        raw_similarity = cosine_similarity(incoming_vector, historical_vector)

        decision_weight = DECISION_WEIGHTS.get(row.decision_type, 0.5)

        adjusted_score = raw_similarity * decision_weight

        if adjusted_score > best_score:
            best_score = adjusted_score
            best_match = row

    if not best_match:
        return None

    return {
        "endpoint": best_match.target_endpoint,
        "tpm": best_match.tpm,
        "confidence": round(float(best_score),4),
        "status": "ROUTED_AI",
        "reason": "AI_ROUTED_HIGH_CONFIDENCE"
    }

def fetch_historical_routes(db, message_type, direction):

    # Guard against missing parameters to avoid SQLAlchemy bind errors
    if not message_type or not direction:
        return []

    # Normalize to match how values are stored in the DB/config (upper-case)
    message_type = message_type.upper()
    direction = direction.upper()

    sql = text(
        """
        SELECT * FROM historical_routes
        WHERE message_type = :message_type AND direction = :direction
        ORDER BY confidence DESC
        LIMIT 200
        """
    )

    result = db.execute(sql, {"message_type": message_type, "direction": direction})
    rows = result.fetchall()

    historical_routes = []

    for row in rows:
        canonical = CanonicalMessage(
            message_type=row[0],
            source_system=row[1],
            receiver_system=row[2],
            format=row[3],
            version=row[4],
            partner_id=row[5],
            control_number=row[6],
            direction=row[7]
        )

        route = HistoricalRoute(
            canonical=canonical,
            target_endpoint=row[8],
            tpm=row[9],
            confidence=row[10],
            decision_type=row[11]
        )

        historical_routes.append(route)
    
    return historical_routes


def is_bucket_mature(history_records):
    strong_decisions = [
        r for r in history_records
        if r.decision_type in ["ROUTED_RULE", "MANUAL_OVERRIDE"]
    ]
    return len(strong_decisions) >= MIN_HISTORY_THRESHOLD

def match(a, b):
    if not a or not b:
        return 0
    return 1 if a == b else 0

def score_rule(rule, canonical):

    weights = CONFIG_CACHE["SIMILARITY_WEIGHTS"]

    score = 0

    score += match(rule["source_system"], canonical.source_system) * weights["source_system"]
    score += match(rule["receiver_system"], canonical.receiver_system) * weights["receiver_system"]
    score += match(rule["version"], canonical.version) * weights["version"]
    score += match(rule.get("message_type"), canonical.message_type) * weights["message_type"]

    return score

def find_best_route(canonical):

    candidates = get_candidate_rules(canonical)

    best_rule = None
    best_score = 0

    for rule in candidates:
        score = score_rule(rule, canonical)

        if score > best_score:
            best_score = score
            best_rule = rule

    return best_rule, best_score

def evaluate_decision(score):

    weights = CONFIG_CACHE["DECISION_WEIGHTS"]

    if score == weights["ROUTED_RULE"]:
        return "ROUTED_RULE"
    else:
        return "ROUTE_FALLBACK"