"""Award-packet export helpers for CivicProcure v0.2.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AwardPacketChecklist:
    solicitation_id: str
    title: str
    format: str
    checklist: tuple[str, ...]
    retention_note: str


def build_award_packet_checklist(
    *, solicitation_id: str, title: str, format: str = "markdown"
) -> AwardPacketChecklist:
    """Build a deterministic award-packet checklist for procurement records."""

    return AwardPacketChecklist(
        solicitation_id=solicitation_id.strip() or "unassigned-solicitation",
        title=title.strip() or "Untitled award packet",
        format=format,
        checklist=(
            "Preserve solicitation, addenda, Q&A, and publication/posting evidence.",
            "Preserve proposal register, evaluation worksheets, conflict disclosures, and exceptions.",
            "Preserve staff recommendation, board memo, award action, and signed agreement.",
            "Preserve records-request notes and retention classification for the procurement file.",
        ),
        retention_note="Keep procurement records according to municipal retention schedule and solicitation terms.",
    )
