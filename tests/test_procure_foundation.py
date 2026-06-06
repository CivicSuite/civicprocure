from fastapi.testclient import TestClient

from civicprocure.award_packet import build_award_packet_checklist
from civicprocure.exception_extract import extract_proposal_exceptions
from civicprocure.main import app
from civicprocure.proposal_compare import compare_proposals
from civicprocure.rfp_draft import draft_rfp_outline
from civicprocure.scoring_summary import build_scoring_summary


client = TestClient(app)


def test_rfp_draft_recommends_owner_and_boundary() -> None:
    result = draft_rfp_outline(
        procurement_title="Public works design services",
        procurement_type="professional services",
        city_need="Bridge inspection and design support.",
    )
    assert result.recommended_owner == "Department lead + Legal + Purchasing"
    assert "Scope of work" in result.sections[1]
    assert "does not evaluate vendors" in result.disclaimer


def test_proposal_comparison_requires_staff_review() -> None:
    result = compare_proposals(
        solicitation_title="Bridge design RFP",
        proposal_summaries=("Vendor A: responsive", "Vendor B: exception noted"),
    )
    assert result.proposal_count == 2
    assert result.staff_review_required is True
    assert "Proposal 1" in result.comparison_rows[0]


def test_exception_extraction_flags_public_records_language() -> None:
    result = extract_proposal_exceptions(
        vendor_name="Acme Consulting",
        proposal_text="This proposal contains proprietary and confidential pricing exceptions.",
    )
    assert result.vendor_name == "Acme Consulting"
    assert any("Confidentiality claim" in flag for flag in result.flags)
    assert result.staff_review_required is True


def test_scoring_summary_defaults_criteria() -> None:
    result = build_scoring_summary(solicitation_title="Bridge design RFP", criteria=())
    assert "Responsiveness" in result.criteria
    assert any("Recommended next action" in section for section in result.summary_sections)


def test_award_packet_preserves_procurement_records_context() -> None:
    result = build_award_packet_checklist(
        title="Bridge design award", solicitation_id="rfp-2026-001"
    )
    assert result.solicitation_id == "rfp-2026-001"
    assert "Preserve solicitation" in result.checklist[0]
    assert "retention schedule" in result.retention_note


def test_procurement_support_apis_success_shape() -> None:
    rfp = client.post(
        "/api/v1/civicprocure/rfps/draft",
        json={
            "procurement_title": "Bridge design RFP",
            "procurement_type": "professional services",
            "city_need": "Bridge inspection and design support.",
        },
    )
    comparison = client.post(
        "/api/v1/civicprocure/proposals/compare",
        json={
            "solicitation_title": "Bridge design RFP",
            "proposal_summaries": ["Vendor A: responsive", "Vendor B: exception noted"],
        },
    )
    exceptions = client.post(
        "/api/v1/civicprocure/proposals/exceptions",
        json={
            "vendor_name": "Acme Consulting",
            "proposal_text": "Proposal includes an indemnification exception.",
        },
    )
    scoring = client.post(
        "/api/v1/civicprocure/scoring/summary",
        json={"solicitation_title": "Bridge design RFP", "criteria": ["Responsiveness"]},
    )
    packet = client.post(
        "/api/v1/civicprocure/award-packet",
        json={"title": "Bridge design award", "solicitation_id": "rfp-2026-001"},
    )
    assert rfp.status_code == 200
    assert rfp.json()["recommended_owner"] == "Department lead + Legal + Purchasing"
    assert rfp.json()["draft_id"]
    assert rfp.json()["staff_review_id"]
    assert comparison.status_code == 200
    assert comparison.json()["proposal_count"] == 2
    assert exceptions.status_code == 200
    assert exceptions.json()["staff_review_required"] is True
    assert scoring.status_code == 200
    assert "Responsiveness" in scoring.json()["criteria"]
    assert packet.status_code == 200
    assert packet.json()["solicitation_id"] == "rfp-2026-001"
    assert packet.json()["packet_id"]
    assert packet.json()["staff_review_id"]


def test_rfp_draft_validation_is_actionable() -> None:
    missing = client.post(
        "/api/v1/civicprocure/rfps/draft",
        json={"procurement_title": "Bridge design RFP", "procurement_type": "professional services"},
    )
    oversized = client.post(
        "/api/v1/civicprocure/rfps/draft",
        json={
            "procurement_title": "Bridge design RFP",
            "procurement_type": "professional services",
            "city_need": "x" * 8001,
        },
    )

    assert missing.status_code == 200
    assert missing.json()["recommended_owner"] == "Department lead + Legal + Purchasing"
    assert oversized.status_code == 422
    assert oversized.json()["detail"]["fields"] == ["city_need"]
    assert "required field names" in oversized.json()["detail"]["fix"]


def test_public_ui_route_is_accessible_and_honest() -> None:
    response = client.get("/civicprocure")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in text
    assert '<main id="main" tabindex="-1">' in text
    assert "v0.2.0 procurement support + staff review queues" in text
    assert "does not evaluate vendors" in text
    assert "procurement system of record" in text


def test_public_ui_uses_local_rfp_api_without_html_injection_sink() -> None:
    text = client.get("/civicprocure").text

    assert 'fetch("/api/v1/civicprocure/rfps/draft"' in text
    assert "result.innerHTML" not in text
    assert "textContent" in text
    assert 'id="draft-button"' in text


def test_staff_ui_route_is_accessible_and_uses_staff_queue_api_without_html_injection_sink() -> None:
    response = client.get("/civicprocure/staff")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert "Procurement review queue" in text
    assert 'fetch("/api/v1/civicprocure/rfps/draft"' in text
    assert 'fetch("/api/v1/civicprocure/award-packet"' in text
    assert 'fetch("/api/v1/civicprocure/staff/reviews"' in text
    assert "X-CivicProcure-Staff-Key" in text
    assert "innerHTML" not in text
    assert "textContent" in text


def test_integration_contracts_advertise_suite_ready_procurement_contracts() -> None:
    response = client.get("/api/v1/civicprocure/integration-contracts")
    assert response.status_code == 200
    payload = response.json()
    contract_names = {contract["name"] for contract in payload["contracts"]}

    assert payload["module"] == "civicprocure"
    assert "civicprocure.rfp_draft.v1" in contract_names
    assert "civicprocure.staff_review_queue.v1" in contract_names
    assert "civicprocure.award_packet.v1" in contract_names
    assert "civicprocure.procurement_context.v1" in contract_names
    assert "civicgrants grant-funded procurement packages" in payload["downstream_ready_for"]
    assert "civiccontracts contract drafting" in payload["downstream_ready_for"]
