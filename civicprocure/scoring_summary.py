"""Scoring summary helpers for CivicProcure v0.1.1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringSummary:
    solicitation_title: str
    criteria: tuple[str, ...]
    summary_sections: tuple[str, ...]
    staff_note: str


def build_scoring_summary(*, solicitation_title: str, criteria: tuple[str, ...]) -> ScoringSummary:
    """Create a board-ready scoring-summary scaffold without ranking vendors."""

    cleaned = tuple(item.strip() for item in criteria if item.strip())
    if not cleaned:
        cleaned = ("Responsiveness", "Qualifications", "Price / value", "References")
    return ScoringSummary(
        solicitation_title=solicitation_title.strip() or "Untitled solicitation",
        criteria=cleaned,
        summary_sections=(
            "Evaluation panel and conflict disclosures.",
            "Responsive proposals received.",
            "Criteria-by-criteria scoring summary.",
            "Exceptions, clarifications, and staff notes.",
            "Recommended next action for governing-body consideration.",
        ),
        staff_note="Staff must preserve scoring worksheets and verify compliance with local procurement policy.",
    )
