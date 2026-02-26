import numpy as np
import json
from app.persistence.db import get_db_connection
from app.models.canonical import RoutingRule, CanonicalMessage, HistoricalRoute
from app.core.config import MIN_HISTORY_THRESHOLD
from app.services.config_cache import CONFIG_CACHE

def build_feature_vector(message):

    vector = []

    MESSAGE_TYPES = CONFIG_CACHE.get("MESSAGE_TYPES", [])
    SYSTEMS = CONFIG_CACHE.get("SYSTEMS", [])
    VERSIONS = CONFIG_CACHE.get("VERSIONS", [])
    DIRECTIONS = CONFIG_CACHE.get("DIRECTIONS", [])
    WEIGHTS = CONFIG_CACHE.get("WEIGHTS", [])

    # Message Type
    for mt in MESSAGE_TYPES:
        value = 1 if message.message_type == mt else 0
        vector.append(value * WEIGHTS["message_type"])

    # Source System
    for sys in SYSTEMS:
        value = 1 if message.source_system == sys else 0
        vector.append(value * WEIGHTS["source_system"])

    # Receiver System
    for sys in SYSTEMS:
        value = 1 if message.receiver_system == sys else 0
        vector.append(value * WEIGHTS["receiver_system"])

    # Version
    for v in VERSIONS:
        value = 1 if message.version == v else 0
        vector.append(value * WEIGHTS["version"])

    # Direction
    for d in DIRECTIONS:
        value = 1 if message.direction == d else 0
        vector.append(value * WEIGHTS["direction"])

    return np.array(vector, dtype=float)


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (
        np.linalg.norm(v1) * np.linalg.norm(v2)
    )

def embedding_route_suggestion(message):

    historical_routes = fetch_historical_routes()

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

def fetch_historical_routes():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""SELECT * FROM historical_routes""")
    rows = cur.fetchall()

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
    

    cur.close()
    conn.close()
    return historical_routes


def is_bucket_mature(history_records):
    strong_decisions = [
        r for r in history_records
        if r.decision_type in ["ROUTED_RULE", "MANUAL_OVERRIDE"]
    ]
    return len(strong_decisions) >= MIN_HISTORY_THRESHOLD