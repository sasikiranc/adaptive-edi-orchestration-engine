from app.models.canonical import CanonicalMessage
from app.services.config_cache import CONFIG_CACHE
from sqlalchemy import text

def get_s4_systems(db):

    if "s4_systems" not in CONFIG_CACHE:

        result = db.execute(
            text("""
                SELECT code
                FROM systems
                WHERE active = TRUE
                AND system_type = 'S4'
            """)
        )

        CONFIG_CACHE["s4_systems"] = [
            row[0].upper() for row in result.fetchall()
        ]

    return CONFIG_CACHE["s4_systems"]

def infer_direction(
    db,
    source_system: str,
    receiver_system: str,
    msg_format: str,
    version: str | None
) -> str:

    source_system = source_system.upper()
    receiver_system = receiver_system.upper()
    msg_format = msg_format.upper()

    systems = get_s4_systems(db)

    if msg_format == "IDOC":

        if source_system in systems:
            return "OUTBOUND"

        if receiver_system in systems:
            return "INBOUND"

    elif msg_format == "X12":

        if not version:
            raise ValueError("X12 message must include version")

        if receiver_system in systems:
            return "INBOUND"

        if source_system in systems:
            return "OUTBOUND"

    raise ValueError(
        f"Unable to infer direction for "
        f"source={source_system}, receiver={receiver_system}, format={msg_format}"
    )

def normalize_idoc_payload(data: dict) -> dict:
    control = data.get("EDI_DC40")

    if not control:
        raise ValueError("Missing EDI_DC40 control record")

    message_type = control.get("MESTYP")
    document_type = control.get("IDOCTYP")
    sender = control.get("SNDPRN")
    receiver = control.get("RCVPRN")
    control_number = control.get("DOCNUM")

    if not all([message_type, sender, receiver, control_number]):
        raise ValueError("Invalid IDOC payload: missing mandatory control fields")

    return {
        "source_system": sender,
        "receiver_system": receiver,
        "format": "IDOC",
        "message_type": message_type,
        "document_type": document_type,
        "partner_id": receiver,  # technical receiver
        "control_number": control_number,
        "version": ""
    }

def normalize_x12_payload(data: dict) -> dict:

    isa = data.get("ISA")
    gs = data.get("GS")
    st = data.get("ST")

    if not all([isa, gs, st]):
        raise ValueError("Invalid X12 payload structure")

    transaction_set = st.get("transaction_set")
    version = gs.get("version")
    control_number = isa.get("control_number")

    sender = data.get("source_system") or isa.get("sender")
    receiver = data.get("receiver_system") or isa.get("receiver")

    if not all([transaction_set, version, control_number, sender, receiver]):
        raise ValueError("Missing required X12 fields")

    return {
        "source_system": sender,
        "receiver_system": receiver,
        "format": "X12",
        "message_type": transaction_set,
        "document_type": None,
        "partner_id": sender,
        "control_number": control_number,
        "version": version
    }

def build_canonical_message(db, raw_data: dict, format_hint: str) -> CanonicalMessage:

    if not format_hint:
        raise ValueError("format_hint is required")

    format_hint = format_hint.upper()

    if format_hint == "IDOC":
        normalized = normalize_idoc_payload(raw_data)

    elif format_hint == "X12":
        normalized = normalize_x12_payload(raw_data)

    else:
        raise ValueError(f"Unsupported format: {format_hint}")

    # Uppercase normalization
    normalized = {
        k: v.upper() if isinstance(v, str) else v
        for k, v in normalized.items()
    }

    direction = infer_direction(
        db,
        normalized["source_system"],
        normalized["receiver_system"],
        normalized["format"],
        normalized.get("version")
    )

    return CanonicalMessage(
        source_system=normalized["source_system"],
        receiver_system=normalized["receiver_system"],
        format=normalized["format"],
        message_type=normalized["message_type"],
        document_type=normalized.get("document_type"),
        partner_id=normalized["partner_id"],
        control_number=normalized["control_number"],
        version=normalized.get("version"),
        direction=direction
    )