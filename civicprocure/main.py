"""FastAPI runtime foundation for CivicProcure."""

import os

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicprocure import __version__
from civicprocure.award_packet import build_award_packet_checklist
from civicprocure.exception_extract import extract_proposal_exceptions
from civicprocure.proposal_compare import compare_proposals
from civicprocure.public_ui import render_public_lookup_page
from civicprocure.rfp_draft import draft_rfp_outline
from civicprocure.scoring_summary import build_scoring_summary
from civicprocure.persistence import (
    ProcureWorkpaperRepository,
    StoredAwardPacket,
    StoredRfpDraft,
)


app = FastAPI(
    title="CivicProcure",
    version=__version__,
    description="Procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo, and award-packet support for CivicSuite.",
)

_workpaper_repository: ProcureWorkpaperRepository | None = None
_workpaper_db_url: str | None = None


class RfpDraftRequest(BaseModel):
    procurement_title: str
    procurement_type: str
    city_need: str = ""


class ProposalCompareRequest(BaseModel):
    solicitation_title: str
    proposal_summaries: list[str]


class ExceptionExtractRequest(BaseModel):
    vendor_name: str
    proposal_text: str


class ScoringSummaryRequest(BaseModel):
    solicitation_title: str
    criteria: list[str]


class AwardPacketRequest(BaseModel):
    solicitation_id: str
    title: str
    format: str = "markdown"


@app.get("/")
def root() -> dict[str, str]:
    """Return current product state without overstating unshipped behavior."""

    return {
        "name": "CivicProcure",
        "version": __version__,
        "status": "procurement support foundation",
        "message": (
            "CivicProcure package, API foundation, sample RFP drafting, proposal comparison, "
            "exception extraction helper, scoring summary helper, award-packet checklist, "
            "optional database-backed RFP/award workpapers, and public UI foundation are online; "
            "live vendor portals, official vendor evaluation decisions, "
            "legal advice, live LLM calls, e-procurement submission portals, and procurement system-of-record integrations "
            "are not implemented yet."
        ),
        "next_step": "Post-v0.1.1 roadmap: local procurement template configuration, CivicContracts links, and staff review queues",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return dependency/version health for deployment smoke checks."""

    return {
        "status": "ok",
        "service": "civicprocure",
        "version": __version__,
        "civiccore_version": CIVICCORE_VERSION,
    }


@app.get("/civicprocure", response_class=HTMLResponse)
def public_civicprocure_page() -> str:
    """Return the public sample procurement support UI."""

    return render_public_lookup_page()


@app.post("/api/v1/civicprocure/rfps/draft")
def rfp_draft(request: RfpDraftRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        return _stored_rfp_response(
            _get_workpaper_repository().create_rfp_draft(
                procurement_title=request.procurement_title,
                procurement_type=request.procurement_type,
                city_need=request.city_need,
            )
        )
    result = draft_rfp_outline(
        procurement_title=request.procurement_title,
        procurement_type=request.procurement_type,
        city_need=request.city_need,
    )
    payload = result.__dict__
    payload["draft_id"] = None
    return payload


@app.get("/api/v1/civicprocure/rfps/draft/{draft_id}")
def get_rfp_draft(draft_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicProcure workpaper persistence is not configured.",
                "fix": "Set CIVICPROCURE_WORKPAPER_DB_URL to retrieve persisted RFP drafts.",
            },
        )
    stored = _get_workpaper_repository().get_rfp_draft(draft_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "RFP draft record not found.",
                "fix": "Use a draft_id returned by POST /api/v1/civicprocure/rfps/draft.",
            },
        )
    return _stored_rfp_response(stored)


@app.post("/api/v1/civicprocure/proposals/compare")
def proposal_compare(request: ProposalCompareRequest) -> dict[str, object]:
    result = compare_proposals(
        solicitation_title=request.solicitation_title,
        proposal_summaries=tuple(request.proposal_summaries),
    )
    return result.__dict__


@app.post("/api/v1/civicprocure/proposals/exceptions")
def proposal_exceptions(request: ExceptionExtractRequest) -> dict[str, object]:
    result = extract_proposal_exceptions(
        vendor_name=request.vendor_name,
        proposal_text=request.proposal_text,
    )
    return result.__dict__


@app.post("/api/v1/civicprocure/scoring/summary")
def scoring_summary(request: ScoringSummaryRequest) -> dict[str, object]:
    result = build_scoring_summary(
        solicitation_title=request.solicitation_title,
        criteria=tuple(request.criteria),
    )
    return result.__dict__


@app.post("/api/v1/civicprocure/award-packet")
def award_packet(request: AwardPacketRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        return _stored_award_packet_response(
            _get_workpaper_repository().create_award_packet(
                solicitation_id=request.solicitation_id,
                title=request.title,
                format=request.format,
            )
        )
    result = build_award_packet_checklist(
        solicitation_id=request.solicitation_id,
        title=request.title,
        format=request.format,
    )
    payload = result.__dict__
    payload["packet_id"] = None
    return payload


@app.get("/api/v1/civicprocure/award-packet/{packet_id}")
def get_award_packet(packet_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicProcure workpaper persistence is not configured.",
                "fix": "Set CIVICPROCURE_WORKPAPER_DB_URL to retrieve persisted award-packet records.",
            },
        )
    stored = _get_workpaper_repository().get_award_packet(packet_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Award-packet record not found.",
                "fix": "Use a packet_id returned by POST /api/v1/civicprocure/award-packet.",
            },
        )
    return _stored_award_packet_response(stored)


def _workpaper_database_url() -> str | None:
    return os.environ.get("CIVICPROCURE_WORKPAPER_DB_URL")


def _get_workpaper_repository() -> ProcureWorkpaperRepository:
    global _workpaper_db_url, _workpaper_repository
    db_url = _workpaper_database_url()
    if db_url is None:
        raise RuntimeError("CIVICPROCURE_WORKPAPER_DB_URL is not configured.")
    if _workpaper_repository is None or db_url != _workpaper_db_url:
        _dispose_workpaper_repository()
        _workpaper_db_url = db_url
        _workpaper_repository = ProcureWorkpaperRepository(db_url=db_url)
    return _workpaper_repository


def _dispose_workpaper_repository() -> None:
    global _workpaper_repository
    if _workpaper_repository is not None:
        _workpaper_repository.engine.dispose()
        _workpaper_repository = None


def _stored_rfp_response(stored: StoredRfpDraft) -> dict[str, object]:
    return {**stored.__dict__, "created_at": stored.created_at.isoformat()}


def _stored_award_packet_response(stored: StoredAwardPacket) -> dict[str, object]:
    return {**stored.__dict__, "created_at": stored.created_at.isoformat()}
