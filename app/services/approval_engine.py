from datetime import datetime

from app.models import ApprovalStatus


def score_risk(phone_number: str, is_blacklisted: bool = False, duplicate_attempts: int = 0) -> int:
    score = 0
    if is_blacklisted:
        score += 100
    if duplicate_attempts > 0:
        score += min(40, duplicate_attempts * 10)
    if not phone_number.startswith("+"):
        score += 10
    return score


def evaluate_status(
    *,
    now: datetime,
    campus_open_hour: int,
    campus_close_hour: int,
    meeting_auto_approve: bool,
    risk_score: int,
) -> ApprovalStatus:
    if risk_score >= 80:
        return ApprovalStatus.REJECTED
    if now.hour < campus_open_hour or now.hour >= campus_close_hour:
        return ApprovalStatus.REJECTED
    if meeting_auto_approve and risk_score < 20:
        return ApprovalStatus.APPROVED
    if risk_score >= 40:
        return ApprovalStatus.REVIEW_REQUIRED
    return ApprovalStatus.PENDING
