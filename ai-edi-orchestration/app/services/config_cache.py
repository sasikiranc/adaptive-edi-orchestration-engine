from sqlalchemy import text
from typing import Dict, Any

CONFIG_CACHE: Dict[str, Any] = {}


def load_config(db):

    config = {}

    # message types
    result = db.execute(text("""
        SELECT code
        FROM message_types
        WHERE active = TRUE
    """))
    config["MESSAGE_TYPES"] = [row[0].upper() for row in result.fetchall()]

    # systems
    result = db.execute(text("""
        SELECT code
        FROM systems
        WHERE active = TRUE
    """))
    config["SYSTEMS"] = [row[0].upper() for row in result.fetchall()]

    # versions
    result = db.execute(text("""
        SELECT code
        FROM versions
        WHERE active = TRUE
    """))
    config["VERSIONS"] = [row[0].upper() for row in result.fetchall()]

    # directions
    result = db.execute(text("""
        SELECT code
        FROM directions
        WHERE active = TRUE
    """))
    config["DIRECTIONS"] = [row[0].upper() for row in result.fetchall()]

    # similarity weights
    result = db.execute(text("""
        SELECT feature_name, weight
        FROM similarity_weights
    """))
    # store similarity weight keys in lower-case so they match how the
    # application code references them (e.g. 'message_type', 'source_system')
    config["SIMILARITY_WEIGHTS"] = {
        row[0].lower(): float(row[1]) for row in result.fetchall()
    }

    # confidence thresholds
    result = db.execute(text("""
        SELECT code, confidence_threshold
        FROM confidence_thresholds
    """))
    config["CONFIDENCE_THRESHOLDS"] = {
        row[0].upper(): float(row[1]) for row in result.fetchall()
    }

    # decision weights
    result = db.execute(text("""
        SELECT decision_type, weight
        FROM decision_weights
    """))
    config["DECISION_WEIGHTS"] = {
        row[0].upper(): float(row[1]) for row in result.fetchall()
    }

    # parnter identity map
    result = db.execute(text("""
        SELECT external_id, format, canonical_system
        FROM partner_identity_map WHERE active = TRUE
    """))
    config["PARTNER_IDENTITY_MAP"] = {
        (row[1].upper(), row[0].upper()): row[2].upper()
        for row in result.fetchall()
    }

    # routing rules
    result = db.execute(text("""
        SELECT message_type,
               direction,
               source_system,
               receiver_system,
               version,
               target_endpoint,
               mapping_id
        FROM routing_rules
        WHERE active = TRUE
    """))

    rules = [dict(row._mapping) for row in result.fetchall()]

    candidate_index = {}

    for r in rules:
        key = (r["message_type"].upper(), r["direction"].upper())

        candidate_index.setdefault(key, []).append(r)

    config["ROUTING_RULES"] = rules
    config["CANDIDATE_INDEX"] = candidate_index

    CONFIG_CACHE.clear()
    CONFIG_CACHE.update(config)

    return CONFIG_CACHE