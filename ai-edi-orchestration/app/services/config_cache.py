from app.persistence.db import get_db_connection

CONFIG_CACHE = {}

def load_config():

    conn = get_db_connection()
    cur = conn.cursor()

    # message types
    cur.execute("SELECT code FROM message_types WHERE active = TRUE")
    message_types = [row[0] for row in cur.fetchall()]

    # systems
    cur.execute("SELECT code FROM systems WHERE active = TRUE")
    systems = [row[0] for row in cur.fetchall()]

    # versions
    cur.execute("SELECT code FROM versions WHERE active = TRUE")
    versions = [row[0] for row in cur.fetchall()]

    # directions
    cur.execute("SELECT code FROM directions WHERE active = TRUE")
    directions = [row[0] for row in cur.fetchall()]

    # similarity weights
    cur.execute("SELECT feature_name, weight FROM similarity_weights")
    weights = {row[0]: row[1] for row in cur.fetchall()}

    # confidence threshold
    cur.execute("SELECT code, confidence_threshold FROM confidence_thresholds")
    confidence_thresholds = {row[0]: row[1] for row in cur.fetchall()}

    # decision weights
    cur.execute("SELECT decision_type, weight FROM decision_weights")
    decision_weights = {row[0]: row[1] for row in cur.fetchall()}

    cur.close()
    conn.close()

    CONFIG_CACHE.update({
        "MESSAGE_TYPES": message_types,
        "SYSTEMS": systems,
        "VERSIONS": versions,
        "DIRECTIONS": directions,
        "WEIGHTS": weights,
        "CONFIDENCE_THRESHOLDS": confidence_thresholds,
        "DECISION_WEIGHTS": decision_weights
    })