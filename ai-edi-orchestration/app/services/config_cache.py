from sqlalchemy import text

CONFIG_CACHE = {}


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
    config["WEIGHTS"] = {
        row[0].upper(): float(row[1]) for row in result.fetchall()
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

    CONFIG_CACHE.clear()
    CONFIG_CACHE.update(config)

    return CONFIG_CACHE