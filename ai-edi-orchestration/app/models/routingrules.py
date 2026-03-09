from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RuleCreate(BaseModel):
    source_system: str
    receiver_system: str
    message_type: str
    partner_id: Optional[str]
    version: Optional[str]
    direction: Optional[str]
    target_endpoint: str
    mapping_id: str
    active: bool

class RuleResponse(RuleCreate):
    id: UUID
    active: bool