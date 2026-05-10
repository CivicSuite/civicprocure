"""Deterministic RFP drafting helpers for CivicProcure v1.0.0."""

from __future__ import annotations

from dataclasses import dataclass


DISCLAIMER = (
    "CivicProcure provides procurement-support drafts only. Staff own every decision; "
    "the module does not evaluate vendors, award contracts, provide legal advice, "
    "submit procurements, or replace the procurement system of record."
)


@dataclass(frozen=True)
class RfpOutline:
    procurement_title: str
    procurement_type: str
    recommended_owner: str
    sections: tuple[str, ...]
    disclaimer: str = DISCLAIMER


def draft_rfp_outline(
    *, procurement_title: str, procurement_type: str, city_need: str = ""
) -> RfpOutline:
    """Return a deterministic RFP outline without live LLM calls or legal drafting."""

    kind = procurement_type.strip().casefold()
    owner = "Purchasing / finance"
    if "construction" in kind or "public works" in kind:
        owner = "Public Works + Purchasing"
    elif "professional" in kind or "consult" in kind:
        owner = "Department lead + Legal + Purchasing"
    elif "technology" in kind or "software" in kind:
        owner = "IT + Purchasing"
    need = city_need.strip() or "Staff-supplied need statement required."
    return RfpOutline(
        procurement_title=procurement_title.strip() or "Untitled procurement",
        procurement_type=procurement_type.strip() or "general",
        recommended_owner=owner,
        sections=(
            f"Purpose and background: {need}",
            "Scope of work and deliverables.",
            "Minimum qualifications and submission requirements.",
            "Evaluation criteria and scoring process.",
            "Required terms, insurance, records, and public-procurement disclosures.",
            "Tentative schedule and award-approval path.",
        ),
    )
