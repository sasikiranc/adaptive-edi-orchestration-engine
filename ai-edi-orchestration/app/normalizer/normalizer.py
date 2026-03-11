from app.models.canonical import CanonicalMessage
from app.services.config_cache import CONFIG_CACHE
from sqlalchemy import text
import json

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

def normalize_idoc_payload(payload: str) -> dict:
    
    try:
        data = json.loads(payload)
    except Exception:
        raise ValueError("Invalid IDOC JSON payload")

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

def normalize_x12_payload(edi_payload: str) -> dict:

    if not edi_payload:
        raise ValueError("Empty X12 payload")

    edi_payload = edi_payload.strip()

    # 1️⃣ Element separator is the 4th character in ISA
    element_sep = edi_payload[3]

    # 2️⃣ Component separator is last char of ISA segment
    isa_end = edi_payload.find("\n")
    if isa_end == -1:
        isa_end = edi_payload.find("GS")

    isa_segment = edi_payload[:isa_end].strip()
    component_sep = isa_segment[-1]

    # 3️⃣ Segment separator = character after ISA
    segment_sep = edi_payload[len(isa_segment)]

    # 4️⃣ Split segments
    segments = [s.strip() for s in edi_payload.split(segment_sep) if s.strip()]

    isa = None
    gs = None
    st = None

    for seg in segments:

        elements = seg.split(element_sep)

        tag = elements[0]

        if tag == "ISA":
            isa = elements

        elif tag == "GS":
            gs = elements

        elif tag == "ST":
            st = elements
            break

    if not isa or not gs or not st:
        raise ValueError("Invalid X12 envelope")

    sender = isa[6].strip()
    receiver = isa[8].strip()
    control_number = isa[13].strip()

    transaction_set = st[1].strip()
    version = gs[8].strip()

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

def build_canonical_message(db, raw_data: str, format_hint: str | None = None) -> CanonicalMessage:

    if not format_hint:
        format_hint = detect_format(raw_data)

    format_hint = format_hint.upper()

    if format_hint == "IDOC":
        if not isinstance(raw_data, dict):
            raise ValueError("IDOC payload must be JSON")

        normalized = normalize_idoc_payload(raw_data)

    elif format_hint == "X12":
        if not isinstance(raw_data, str):
            raise ValueError("X12 payload must be raw string")

        normalized = normalize_x12_payload(raw_data)

    else:
        raise ValueError(f"Unsupported format: {format_hint}")

    # Uppercase normalization
    normalized = {
        k: v.upper() if isinstance(v, str) else v
        for k, v in normalized.items()
    }

    normalized["source_system"] = map_partner_system(
        normalized["source_system"],
        normalized["format"]
    )

    normalized["receiver_system"] = map_partner_system(
        normalized["receiver_system"],
        normalized["format"]
    )

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

def detect_format(payload: str) -> str:

    payload = payload.strip()

    if payload.startswith("ISA"):
        return "X12"

    if payload.startswith("UNA") or payload.startswith("UNB"):
        return "EDIFACT"

    if payload.startswith("{") or payload.startswith("["):
        if "EDI_DC40" in payload:
            return "IDOC"

    raise ValueError("Unable to detect message format")


def map_partner_system(system_id: str, format: str) -> str:

    key = (format.upper(), system_id.upper())

    mapped = CONFIG_CACHE["PARTNER_IDENTITY_MAP"].get(key)

    if not mapped:
        raise ValueError(f"Unknown system identifier: {system_id} ({format})")

    return mapped