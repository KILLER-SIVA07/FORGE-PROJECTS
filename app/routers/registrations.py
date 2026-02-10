from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_roles
from app.models import ApprovalLog, ApprovalStatus, Event, Registration, Role, User
from app.schemas import RegistrationCreate, RegistrationOut
from app.services.approval_engine import evaluate_status, score_risk

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.post("", response_model=RegistrationOut)
def create_registration(payload: RegistrationCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == payload.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    duplicate_attempts = db.query(Registration).filter(
        Registration.event_id == payload.event_id,
        Registration.phone_number == payload.phone_number,
    ).count()
    risk = score_risk(payload.phone_number, duplicate_attempts=duplicate_attempts)
    status = evaluate_status(
        now=datetime.utcnow(),
        campus_open_hour=8,
        campus_close_hour=20,
        meeting_auto_approve=event.approval_type == "auto",
        risk_score=risk,
    )
    reg = Registration(**payload.model_dump(), risk_score=risk, status=status)
    db.add(reg)
    db.commit()
    db.refresh(reg)

    log = ApprovalLog(
        registration_id=reg.id,
        level=1,
        decision=status.value,
        reason="Policy engine initial decision",
        actor_id=None,
    )
    db.add(log)
    db.commit()
    return reg


@router.post("/{registration_id}/decision", response_model=RegistrationOut)
def manual_decision(
    registration_id: int,
    decision: str,
    reason: str = "",
    user: User = Depends(require_roles(Role.STAFF, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Decision must be approved or rejected")

    reg.status = ApprovalStatus.APPROVED if decision == "approved" else ApprovalStatus.REJECTED
    db.add(
        ApprovalLog(
            registration_id=reg.id,
            level=3 if user.role == Role.ADMIN else 1,
            decision=decision,
            reason=reason,
            actor_id=user.id,
        )
    )
    db.commit()
    db.refresh(reg)
    return reg


@router.get("/mine", response_model=list[RegistrationOut])
def my_registrations(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Registration).order_by(Registration.created_at.desc()).limit(100).all()
