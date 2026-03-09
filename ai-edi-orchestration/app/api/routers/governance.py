from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.governance_service import manual_override
from app.core.security import validate_admin_token, validate_token
from app.persistence.db import get_db
from app.persistence.db import SessionLocal
from fastapi import Request, Depends
from sqlalchemy.orm import Session

router = APIRouter()

class ManualOverrideRequest(BaseModel):
    control_number: str
    target_endpoint: str
    tpm_mapping_id: str


@router.post("/governance/manual-override")
def override(request: ManualOverrideRequest, db: Session = Depends(get_db), user=Depends(validate_token)):
    return manual_override(
        db,
        request.control_number,
        request.target_endpoint,
        request.tpm_mapping_id
    )