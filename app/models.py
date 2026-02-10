import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    SECURITY = "security"
    STAFF = "staff"
    VISITOR = "visitor"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), index=True)
    department: Mapped[str] = mapped_column(String(100), default="general")


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    department: Mapped[str] = mapped_column(String(100), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)
    visitor_limit: Mapped[int] = mapped_column(Integer, default=100)
    approval_type: Mapped[str] = mapped_column(String(30), default="manual")


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (UniqueConstraint("event_id", "phone_number", name="uq_event_phone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(30), index=True)
    register_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str] = mapped_column(String(100))
    purpose: Mapped[str] = mapped_column(String(255), default="event")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event = relationship("Event")


class ApprovalLog(Base):
    __tablename__ = "approval_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id"), index=True)
    level: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text, default="")
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CheckLog(Base):
    __tablename__ = "check_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id"), index=True)
    action: Mapped[str] = mapped_column(String(20), index=True)
    gate_id: Mapped[str] = mapped_column(String(50), default="main-gate")
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
