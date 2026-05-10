"""Proposal exception extraction helpers for CivicProcure v1.0.0."""

from __future__ import annotations

from dataclasses import dataclass

from civicprocure.rfp_draft import DISCLAIMER


@dataclass(frozen=True)
class ProposalExceptions:
    vendor_name: str
    flags: tuple[str, ...]
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


def extract_proposal_exceptions(*, vendor_name: str, proposal_text: str) -> ProposalExceptions:
    """Flag common exception language without making a legal determination."""

    text = proposal_text.casefold()
    flags: list[str] = []
    if "exception" in text or "deviation" in text:
        flags.append("Proposal appears to contain exception/deviation language.")
    if "indemn" in text:
        flags.append("Indemnification language requires legal review.")
    if "insurance" in text:
        flags.append("Insurance language should be compared to solicitation requirements.")
    if "confidential" in text or "proprietary" in text:
        flags.append("Confidentiality claim should be reviewed against public-records obligations.")
    if not flags:
        flags.append("No common exception keywords found; staff must still review the full proposal.")
    return ProposalExceptions(
        vendor_name=vendor_name.strip() or "Unnamed vendor",
        flags=tuple(flags),
        staff_review_required=True,
    )
