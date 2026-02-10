from datetime import datetime

from pydantic import BaseModel, Field

from app.models import ApprovalStatus, Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=8)
    role: Role
    department: str = "general"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: Role
    department: str

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class EventCreate(BaseModel):
    name: str
    department: str
    starts_at: datetime
    ends_at: datetime
    visitor_limit: int = 100
    approval_type: str = "manual"


class EventOut(EventCreate):
    id: int

    model_config = {"from_attributes": True}


class RegistrationCreate(BaseModel):
    event_id: int
    name: str
    phone_number: str
    register_number: str | None = None
    department: str
    purpose: str = "event"


class RegistrationOut(BaseModel):
    id: int
    event_id: int
    name: str
    phone_number: str
    department: str
    purpose: str
    risk_score: int
    status: ApprovalStatus

    model_config = {"from_attributes": True}


class GateAction(BaseModel):
    registration_id: int
    gate_id: str = "main-gate"
    action: str = Field(pattern="^(checkin|checkout|reject)$")
