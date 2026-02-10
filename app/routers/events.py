from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import Event, Role, User
from app.schemas import EventCreate, EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventOut)
def create_event(
    payload: EventCreate,
    _: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.starts_at.desc()).all()
