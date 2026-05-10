"""Adversarial local integration contracts for CivicProcure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IntegrationMockResult:
    scenario: str
    status: str
    review_required: bool
    findings: tuple[str, ...]
    boundary: str


def validate_procurement_context_mocks(payload: dict[str, Any]) -> IntegrationMockResult:
    """Validate local procurement context payloads without external calls."""

    findings: list[str] = []
    scenario = str(payload.get("scenario", "procurement-context"))

    if payload.get("role") not in {"staff", "service"}:
        findings.append("Rejected procurement context without trusted staff or service role.")
    if not payload.get("solicitation_context_id"):
        findings.append("Missing solicitation context ID; preserve the procurement file before review.")
    if not payload.get("clerk_context_id"):
        findings.append("Missing CivicClerk context ID; cite board or agenda context before award packets.")
    if payload.get("official_vendor_evaluation") is True:
        findings.append("Rejected attempted official vendor evaluation in integration context.")
    if payload.get("award_decision") is True:
        findings.append("Rejected attempted award decision in integration context.")
    if payload.get("procurement_submitted") is True:
        findings.append("Rejected attempted procurement submission in integration context.")
    if payload.get("legal_advice") is True:
        findings.append("Rejected legal-advice claim in procurement integration context.")
    if payload.get("vendor_portal_source") == "live":
        findings.append("Rejected live vendor-portal claim; v1.0.0 uses local deterministic context only.")
    if payload.get("source_date_status") == "stale":
        findings.append("Stale procurement context requires staff refresh before comparison or award packets.")

    status = "ready-for-staff-review" if not findings else "blocked-for-staff-review"
    return IntegrationMockResult(
        scenario=scenario,
        status=status,
        review_required=True,
        findings=tuple(findings),
        boundary=(
            "CivicProcure validates local integration context only; it does not call live "
            "CivicClerk, CivicContracts, vendor portal, LLM, legal, award, submission, "
            "or procurement system-of-record services in v1.0.0."
        ),
    )
