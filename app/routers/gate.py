from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import ApprovalStatus, CheckLog, Registration, Role, User
from app.schemas import GateAction

router = APIRouter(prefix="/gate", tags=["gate"])


@router.post("/action")
def gate_action(
    payload: GateAction,
    user: User = Depends(require_roles(Role.SECURITY, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    reg = db.query(Registration).filter(Registration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if payload.action == "checkin" and reg.status != ApprovalStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Visitor is not approved for check-in")

    log = CheckLog(
        registration_id=payload.registration_id,
        action=payload.action,
        gate_id=payload.gate_id,
        actor_id=user.id,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return {"ok": True, "registration_id": payload.registration_id, "action": payload.action}
