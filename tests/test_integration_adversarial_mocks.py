from fastapi.testclient import TestClient

from civicprocure.integration_mocks import validate_procurement_context_mocks
from civicprocure.main import app


client = TestClient(app)


def test_adversarial_mock_rejects_spoofed_award_and_missing_context() -> None:
    result = validate_procurement_context_mocks(
        {
            "scenario": "spoofed-award-decision",
            "role": "vendor",
            "official_vendor_evaluation": True,
            "award_decision": True,
            "procurement_submitted": True,
            "legal_advice": True,
            "vendor_portal_source": "live",
            "source_date_status": "stale",
        }
    )

    assert result.status == "blocked-for-staff-review"
    assert result.review_required is True
    assert "Rejected procurement context without trusted staff or service role." in result.findings
    assert "Rejected attempted official vendor evaluation in integration context." in result.findings
    assert "Rejected attempted award decision in integration context." in result.findings
    assert "does not call live CivicClerk" in result.boundary


def test_integration_mock_api_accepts_complete_staff_context_for_review() -> None:
    response = client.post(
        "/api/v1/civicprocure/integrations/mock/procurement-context",
        json={
            "scenario": "complete-local-context",
            "role": "staff",
            "solicitation_context_id": "solicitation-123",
            "clerk_context_id": "agenda-item-456",
            "contract_context_id": "contract-template-789",
            "source_date_status": "current",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready-for-staff-review"
    assert payload["findings"] == []
    assert payload["review_required"] is True


def test_integration_mock_api_blocks_stale_or_partial_context() -> None:
    response = client.post(
        "/api/v1/civicprocure/integrations/mock/procurement-context",
        json={
            "scenario": "stale-procurement-context",
            "role": "service",
            "solicitation_context_id": "solicitation-123",
            "source_date_status": "stale",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked-for-staff-review"
    assert "Missing CivicClerk context ID" in " ".join(payload["findings"])
    assert "Stale procurement context" in " ".join(payload["findings"])


def test_procurement_review_context_carries_clerk_and_contract_references() -> None:
    response = client.post(
        "/api/v1/civicprocure/context/procurement-review",
        json={
            "solicitation_id": "rfp-2026-001",
            "procurement_title": "Bridge design RFP",
            "solicitation_context_id": "solicitation-123",
            "clerk_context_id": "agenda-item-456",
            "contract_context_id": "contract-template-789",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["solicitation_id"] == "rfp-2026-001"
    assert payload["review_required"] is True
    assert "CivicClerk context: agenda-item-456" in payload["citations"]
    assert "CivicContracts context: contract-template-789" in payload["citations"]
    assert "not an official vendor evaluation" in payload["boundary"]
