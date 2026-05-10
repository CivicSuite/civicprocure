"""Proposal comparison helpers for CivicProcure v1.0.0."""

from __future__ import annotations

from dataclasses import dataclass

from civicprocure.rfp_draft import DISCLAIMER


@dataclass(frozen=True)
class ProposalComparison:
    solicitation_title: str
    proposal_count: int
    comparison_rows: tuple[str, ...]
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


def compare_proposals(
    *, solicitation_title: str, proposal_summaries: tuple[str, ...]
) -> ProposalComparison:
    """Build a neutral comparison scaffold; staff perform actual evaluation."""

    cleaned = tuple(summary.strip() for summary in proposal_summaries if summary.strip())
    rows = tuple(
        f"Proposal {idx}: summarize responsiveness, exceptions, price factors, and review notes."
        for idx, _summary in enumerate(cleaned, start=1)
    )
    if not rows:
        rows = ("No proposal summaries supplied; staff must add submissions before comparison.",)
    return ProposalComparison(
        solicitation_title=solicitation_title.strip() or "Untitled solicitation",
        proposal_count=len(cleaned),
        comparison_rows=rows,
        staff_review_required=True,
    )
