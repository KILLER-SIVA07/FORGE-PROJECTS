from datetime import datetime

from app.models import ApprovalStatus
from app.services.approval_engine import evaluate_status, score_risk


def test_blacklist_risk_rejected():
    risk = score_risk("+911234567890", is_blacklisted=True)
    assert risk >= 100
    status = evaluate_status(
        now=datetime(2026, 1, 1, 10, 0, 0),
        campus_open_hour=8,
        campus_close_hour=20,
        meeting_auto_approve=True,
        risk_score=risk,
    )
    assert status == ApprovalStatus.REJECTED


def test_auto_approve_low_risk_meeting_hour():
    risk = score_risk("+911234567890")
    status = evaluate_status(
        now=datetime(2026, 1, 1, 11, 0, 0),
        campus_open_hour=8,
        campus_close_hour=20,
        meeting_auto_approve=True,
        risk_score=risk,
    )
    assert status == ApprovalStatus.APPROVED
