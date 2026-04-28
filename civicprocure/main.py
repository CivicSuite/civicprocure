"""FastAPI runtime foundation for CivicProcure."""

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicprocure import __version__
from civicprocure.award_packet import build_award_packet_checklist
from civicprocure.exception_extract import extract_proposal_exceptions
from civicprocure.proposal_compare import compare_proposals
from civicprocure.public_ui import render_public_lookup_page
from civicprocure.rfp_draft import draft_rfp_outline
from civicprocure.scoring_summary import build_scoring_summary


app = FastAPI(
    title="CivicProcure",
    version=__version__,
    description="Procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo, and award-packet support for CivicSuite.",
)


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
            "and public UI foundation are online; live vendor portals, official vendor evaluation decisions, "
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
    result = draft_rfp_outline(
        procurement_title=request.procurement_title,
        procurement_type=request.procurement_type,
        city_need=request.city_need,
    )
    return result.__dict__


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
    result = build_award_packet_checklist(
        solicitation_id=request.solicitation_id,
        title=request.title,
        format=request.format,
    )
    return result.__dict__
