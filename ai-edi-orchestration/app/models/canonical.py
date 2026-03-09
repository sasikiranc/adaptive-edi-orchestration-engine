from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class RoutingRule:
    message_type: str
    source_system: str
    receiver_system: str
    version: Optional[str]

    endpoint: str
    tpm_mapping_id: str
    active: bool = True

@dataclass
class AIRoutingSuggestion:
    suggested_endpoint: str
    suggested_tpm: str
    confidence: float
    reasoning: str

@dataclass
class ManualOverride:
    control_number: str
    original_suggestion: str
    corrected_endpoint: str
    corrected_tpm: str
    user_id: str
    timestamp: str

class CanonicalMessage(BaseModel):
    # Technical routing context
    source_system: str              # e.g. S4, PARTNER, CPI
    receiver_system: str            # Logical communication target
    format: str                     # IDOC, X12

    # Business document context
    message_type: str               # DESADV, INVOIC, ORDERS, etc.
    document_type: Optional[str] = None  # e.g. ORDERS05 (for IDoc)

    # Business partner context
    partner_id: str                 # Logical business partner

    # Control & versioning
    control_number: str             # ISA control number or IDoc DOCNUM
    version: Optional[str] = None   # 4010, 5010, etc.

    # Derived internally
    direction: str                  # INBOUND / OUTBOUND (computed, not user-provided)

class HistoricalRoute:
    def __init__(
        self,
        canonical: CanonicalMessage,
        target_endpoint: str,
        tpm: str,
        confidence: float,
        decision_type: str
    ):
        self.canonical = canonical
        self.target_endpoint = target_endpoint
        self.tpm = tpm
        self.confidence = confidence
        self.decision_type = decision_type