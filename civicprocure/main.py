"""FastAPI runtime foundation for CivicProcure."""

import os

from civiccore import __version__ as CIVICCORE_VERSION
from civiccore.auth import staff_key_gate
from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from civicprocure import __version__
from civicprocure.award_packet import build_award_packet_checklist
from civicprocure.exception_extract import extract_proposal_exceptions
from civicprocure.integration_mocks import validate_procurement_context_mocks
from civicprocure.proposal_compare import compare_proposals
from civicprocure.public_ui import render_public_lookup_page
from civicprocure.rfp_draft import draft_rfp_outline
from civicprocure.scoring_summary import build_scoring_summary
from civicprocure.persistence import (
    ProcureWorkpaperRepository,
    StaffReviewQueueItem,
    StaffReviewSummary,
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
_require_staff_key = staff_key_gate("CIVICPROCURE_STAFF_API_KEY", "X-CivicProcure-Staff-Key")


class RfpDraftRequest(BaseModel):
    procurement_title: str = Field(..., min_length=1, max_length=500)
    procurement_type: str = Field(..., min_length=1, max_length=160)
    city_need: str = Field(default="", max_length=8000)


class ProposalCompareRequest(BaseModel):
    solicitation_title: str = Field(..., min_length=1, max_length=500)
    proposal_summaries: list[str] = Field(..., min_length=1, max_length=25)


class ExceptionExtractRequest(BaseModel):
    vendor_name: str = Field(..., min_length=1, max_length=255)
    proposal_text: str = Field(..., min_length=1, max_length=8000)


class ScoringSummaryRequest(BaseModel):
    solicitation_title: str = Field(..., min_length=1, max_length=500)
    criteria: list[str] = Field(default_factory=list, max_length=25)


class AwardPacketRequest(BaseModel):
    solicitation_id: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    format: str = Field(default="markdown", max_length=40)


class ProcurementContextRequest(BaseModel):
    solicitation_id: str = Field(..., min_length=1, max_length=255)
    procurement_title: str = Field(..., min_length=1, max_length=500)
    solicitation_context_id: str = Field(default="", max_length=255)
    clerk_context_id: str = Field(default="", max_length=255)
    contract_context_id: str = Field(default="", max_length=255)
    source_date_status: str = Field(default="current", max_length=80)


class IntegrationMockRequest(BaseModel):
    scenario: str = Field(default="procurement-context", max_length=160)
    role: str = Field(default="staff", max_length=80)
    solicitation_context_id: str = Field(default="", max_length=255)
    clerk_context_id: str = Field(default="", max_length=255)
    contract_context_id: str = Field(default="", max_length=255)
    official_vendor_evaluation: bool = False
    award_decision: bool = False
    procurement_submitted: bool = False
    legal_advice: bool = False
    vendor_portal_source: str = Field(default="local", max_length=160)
    source_date_status: str = Field(default="current", max_length=80)


class StaffReviewCreateRequest(BaseModel):
    procurement_title: str = Field(..., min_length=1, max_length=500)
    reason: str = Field(..., min_length=1, max_length=1000)
    solicitation_id: str | None = Field(default=None, max_length=255)


class StaffReviewUpdateRequest(BaseModel):
    status: str = Field(..., min_length=1, max_length=120)
    assigned_to: str | None = Field(default=None, max_length=255)
    resolution: str | None = Field(default=None, max_length=2000)


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
            "optional database-backed RFP/award workpapers, staff review queues, review-required "
            "CivicClerk/CivicContracts context packets, adversarial local integration mocks, readiness gate, and public UI foundation are online; "
            "live vendor portals, official vendor evaluation decisions, "
            "legal advice, live LLM calls, e-procurement submission portals, award decisions, and procurement system-of-record integrations "
            "are not implemented."
        ),
        "next_step": "Configure CIVICPROCURE_WORKPAPER_DB_URL and verify /ready before public use.",
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


@app.get("/ready")
def ready() -> dict[str, object]:
    return _readiness_payload()


@app.get("/api/v1/civicprocure/readiness")
def readiness() -> dict[str, object]:
    return _readiness_payload()


@app.get("/civicprocure", response_class=HTMLResponse)
def public_civicprocure_page() -> str:
    """Return the public sample procurement support UI."""

    return render_public_lookup_page()


@app.post("/api/v1/civicprocure/rfps/draft")
def rfp_draft(request: RfpDraftRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        stored = _get_workpaper_repository().create_rfp_draft(
            procurement_title=request.procurement_title,
            procurement_type=request.procurement_type,
            city_need=request.city_need,
        )
        staff_review = _get_workpaper_repository().create_staff_review_queue_item(
            procurement_title=stored.procurement_title,
            solicitation_id=stored.draft_id,
            reason="RFP draft requires staff review before publication, proposal evaluation, or award action.",
            created_by="staff",
        )
        return _stored_rfp_response(stored, staff_review=staff_review)
    result = draft_rfp_outline(
        procurement_title=request.procurement_title,
        procurement_type=request.procurement_type,
        city_need=request.city_need,
    )
    payload = result.__dict__
    payload["draft_id"] = None
    payload["staff_review_id"] = None
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
        stored = _get_workpaper_repository().create_award_packet(
            solicitation_id=request.solicitation_id,
            title=request.title,
            format=request.format,
        )
        staff_review = _get_workpaper_repository().create_staff_review_queue_item(
            procurement_title=stored.title,
            solicitation_id=stored.solicitation_id,
            reason="Award packet requires staff review before governing-body action or contract routing.",
            created_by="staff",
        )
        return _stored_award_packet_response(stored, staff_review=staff_review)
    result = build_award_packet_checklist(
        solicitation_id=request.solicitation_id,
        title=request.title,
        format=request.format,
    )
    payload = result.__dict__
    payload["packet_id"] = None
    payload["staff_review_id"] = None
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


@app.post("/api/v1/civicprocure/context/procurement-review")
def procurement_review_context(request: ProcurementContextRequest) -> dict[str, object]:
    rfp = draft_rfp_outline(
        procurement_title=request.procurement_title,
        procurement_type="general",
    )
    citations = [f"Procurement draft context: {rfp.recommended_owner}"]
    if request.solicitation_context_id:
        citations.append(f"Solicitation context: {request.solicitation_context_id}")
    if request.clerk_context_id:
        citations.append(f"CivicClerk context: {request.clerk_context_id}")
    if request.contract_context_id:
        citations.append(f"CivicContracts context: {request.contract_context_id}")
    return {
        "solicitation_id": request.solicitation_id.strip() or "unassigned-solicitation",
        "procurement_title": request.procurement_title.strip() or "Untitled procurement",
        "solicitation_context_id": request.solicitation_context_id,
        "clerk_context_id": request.clerk_context_id,
        "contract_context_id": request.contract_context_id,
        "source_date_status": request.source_date_status,
        "citations": citations,
        "recommended_owner": rfp.recommended_owner,
        "review_required": True,
        "boundary": (
            "CivicProcure provides procurement review context only; it is not an official vendor "
            "evaluation, award decision, legal opinion, procurement submission, live vendor-portal "
            "result, or procurement system-of-record action."
        ),
    }


@app.post("/api/v1/civicprocure/integrations/mock/procurement-context")
def integration_mock_procurement_context(request: IntegrationMockRequest) -> dict[str, object]:
    result = validate_procurement_context_mocks(request.model_dump())
    return {
        "scenario": result.scenario,
        "status": result.status,
        "review_required": result.review_required,
        "findings": list(result.findings),
        "boundary": result.boundary,
    }


@app.post("/api/v1/civicprocure/staff/reviews")
def create_staff_review(
    request: StaffReviewCreateRequest,
    _staff_principal: object = Depends(_require_staff_key),
) -> dict[str, object]:
    _require_persistence_configured()
    item = _get_workpaper_repository().create_staff_review_queue_item(
        procurement_title=request.procurement_title,
        solicitation_id=request.solicitation_id,
        reason=request.reason,
        created_by="staff",
    )
    return _staff_review_payload(item)


@app.get("/api/v1/civicprocure/staff/reviews")
def list_staff_reviews(
    status: str | None = None,
    _staff_principal: object = Depends(_require_staff_key),
) -> dict[str, object]:
    _require_persistence_configured()
    return {
        "visibility": "staff_only",
        "items": [
            _staff_review_payload(item)
            for item in _get_workpaper_repository().list_staff_review_queue_items(status=status)
        ],
    }


@app.patch("/api/v1/civicprocure/staff/reviews/{review_id}")
def update_staff_review(
    review_id: str,
    request: StaffReviewUpdateRequest,
    _staff_principal: object = Depends(_require_staff_key),
) -> dict[str, object]:
    _require_persistence_configured()
    try:
        item = _get_workpaper_repository().update_staff_review_queue_item(
            review_id=review_id,
            status=request.status,
            assigned_to=request.assigned_to,
            resolution=request.resolution,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": "Staff review update is invalid.", "fix": str(exc)},
        ) from exc
    if item is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "CivicProcure staff review item was not found.",
                "fix": "List staff reviews and retry with an existing review_id.",
            },
        )
    return _staff_review_payload(item)


@app.get("/api/v1/civicprocure/staff/reviews/summary")
def staff_review_summary(
    _staff_principal: object = Depends(_require_staff_key),
) -> dict[str, object]:
    _require_persistence_configured()
    return _staff_review_summary_payload(_get_workpaper_repository().staff_review_summary())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: object, exc: RequestValidationError) -> JSONResponse:
    fields = sorted(
        {
            str(error["loc"][-1])
            for error in exc.errors()
            if error.get("loc") and error["loc"][0] in {"body", "query", "path"}
        }
    )
    field_text = ", ".join(fields) if fields else "request"
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "message": f"CivicProcure could not validate: {field_text}.",
                "fix": (
                    "Send a JSON body with the required field names listed in the fields array. "
                    "Keep text fields within documented bounds and use booleans for yes/no inputs."
                ),
                "fields": fields,
            }
        },
    )


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


def _stored_rfp_response(
    stored: StoredRfpDraft, *, staff_review: StaffReviewQueueItem | None = None
) -> dict[str, object]:
    return {
        **stored.__dict__,
        "staff_review_id": None if staff_review is None else staff_review.review_id,
        "created_at": stored.created_at.isoformat(),
    }


def _stored_award_packet_response(
    stored: StoredAwardPacket, *, staff_review: StaffReviewQueueItem | None = None
) -> dict[str, object]:
    return {
        **stored.__dict__,
        "staff_review_id": None if staff_review is None else staff_review.review_id,
        "created_at": stored.created_at.isoformat(),
    }


def _require_persistence_configured() -> None:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicProcure staff review persistence is not configured.",
                "fix": "Set CIVICPROCURE_WORKPAPER_DB_URL before using staff review queue routes.",
            },
        )


def _staff_review_payload(item: StaffReviewQueueItem) -> dict[str, object]:
    return {
        "review_id": item.review_id,
        "solicitation_id": item.solicitation_id,
        "procurement_title": item.procurement_title,
        "status": item.status,
        "reason": item.reason,
        "assigned_to": item.assigned_to,
        "resolution": item.resolution,
        "created_by": item.created_by,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
        "visibility": item.visibility,
        "boundary": (
            "Staff review queues support procurement triage only; they do not evaluate vendors, "
            "award contracts, submit procurements, provide legal advice, or update a procurement system of record."
        ),
    }


def _staff_review_summary_payload(summary: StaffReviewSummary) -> dict[str, object]:
    return {
        "total_items": summary.total_items,
        "by_status": summary.by_status,
        "open_items": summary.open_items,
        "generated_at": summary.generated_at.isoformat(),
        "visibility": summary.visibility,
    }


def _readiness_payload() -> dict[str, object]:
    db_url = _workpaper_database_url()
    if db_url is None:
        return {
            "status": "not-ready",
            "ready": False,
            "workpaper_database_configured": False,
            "schema_ready": False,
            "schema_version": None,
            "expected_schema_version": None,
            "blockers": ["Set CIVICPROCURE_WORKPAPER_DB_URL to a local workpaper database."],
        }

    repository = _get_workpaper_repository()
    schema_status = repository.schema_status()
    blockers: list[str] = []
    if not schema_status.ready:
        blockers.append("Initialize the CivicProcure workpaper database schema with civicprocure-db-status.")
    ready_for_public_use = not blockers
    return {
        "status": "ready" if ready_for_public_use else "not-ready",
        "ready": ready_for_public_use,
        "workpaper_database_configured": True,
        "schema_ready": schema_status.ready,
        "schema_version": schema_status.schema_version,
        "expected_schema_version": schema_status.expected_schema_version,
        "blockers": blockers,
    }
