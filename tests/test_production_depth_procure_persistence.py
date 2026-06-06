from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from civicprocure.main import app, _dispose_workpaper_repository
from civicprocure.persistence import ProcureWorkpaperRepository


client = TestClient(app)


def test_repository_persists_rfp_and_award_packet(tmp_path: Path) -> None:
    db_path = tmp_path / "civicprocure.db"
    repo = ProcureWorkpaperRepository(db_url=f"sqlite+pysqlite:///{db_path.as_posix()}")
    rfp = repo.create_rfp_draft(
        procurement_title="Bridge design RFP",
        procurement_type="professional services",
        city_need="Bridge inspection and design support.",
    )
    packet = repo.create_award_packet(
        solicitation_id="rfp-2026-001",
        title="Bridge design award",
        format="markdown",
    )
    repo.engine.dispose()

    reloaded = ProcureWorkpaperRepository(db_url=f"sqlite+pysqlite:///{db_path.as_posix()}")
    assert reloaded.get_rfp_draft(rfp.draft_id).recommended_owner == (
        "Department lead + Legal + Purchasing"
    )
    assert reloaded.get_award_packet(packet.packet_id).solicitation_id == "rfp-2026-001"
    reloaded.engine.dispose()
    db_path.unlink()


def test_workpaper_repository_records_schema_status(tmp_path: Path) -> None:
    db_path = tmp_path / "schema-status.db"
    repo = ProcureWorkpaperRepository(db_url=f"sqlite+pysqlite:///{db_path.as_posix()}")
    try:
        status = repo.schema_status()
    finally:
        repo.engine.dispose()

    assert status.ready is True
    assert status.schema_version == status.expected_schema_version
    assert status.missing_tables == ()


def test_db_status_cli_reports_ready_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "cli-status.db"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "civicprocure.db_admin",
            "--db-url",
            f"sqlite+pysqlite:///{db_path.as_posix()}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "CivicProcure schema ready" in result.stdout


def test_readiness_uses_default_local_workpaper_database(monkeypatch) -> None:
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()

    response = client.get("/api/v1/civicprocure/readiness")

    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["ready"] is True
    assert payload["workpaper_database_configured"] is True
    assert payload["using_default_local_database"] is True
    assert payload["schema_ready"] is True
    assert payload["blockers"] == []
    assert "civicprocure-workpapers.db" in payload["workpaper_database_url"]


def test_readiness_passes_with_configured_workpaper_database(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "ready-runtime.db"
    monkeypatch.setenv(
        "CIVICPROCURE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}"
    )
    _dispose_workpaper_repository()

    try:
        response = client.get("/ready")
    finally:
        _dispose_workpaper_repository()
        monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL")

    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["ready"] is True
    assert payload["schema_ready"] is True


def test_procure_persistence_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicprocure-api.db"
    monkeypatch.setenv(
        "CIVICPROCURE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}"
    )
    _dispose_workpaper_repository()
    rfp = client.post(
        "/api/v1/civicprocure/rfps/draft",
        json={
            "procurement_title": "Bridge design RFP",
            "procurement_type": "professional services",
            "city_need": "Bridge inspection and design support.",
        },
    )
    fetched_rfp = client.get(f"/api/v1/civicprocure/rfps/draft/{rfp.json()['draft_id']}")
    packet = client.post(
        "/api/v1/civicprocure/award-packet",
        json={"title": "Bridge design award", "solicitation_id": "rfp-2026-001"},
    )
    fetched_packet = client.get(f"/api/v1/civicprocure/award-packet/{packet.json()['packet_id']}")
    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL")

    assert fetched_rfp.status_code == 200
    assert fetched_rfp.json()["recommended_owner"] == "Department lead + Legal + Purchasing"
    assert fetched_packet.status_code == 200
    assert fetched_packet.json()["solicitation_id"] == "rfp-2026-001"
    db_path.unlink()


def test_rfp_and_award_persistence_create_staff_review_queue(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicprocure-staff-review.db"
    monkeypatch.setenv(
        "CIVICPROCURE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}"
    )
    monkeypatch.setenv("CIVICPROCURE_STAFF_API_KEY", "test-staff-key")
    _dispose_workpaper_repository()

    headers = {"X-CivicProcure-Role": "staff", "X-CivicProcure-Staff-Key": "test-staff-key"}
    rfp = client.post(
        "/api/v1/civicprocure/rfps/draft",
        json={
            "procurement_title": "Bridge design RFP",
            "procurement_type": "professional services",
            "city_need": "Bridge inspection and design support.",
        },
    )
    packet = client.post(
        "/api/v1/civicprocure/award-packet",
        json={"title": "Bridge design award", "solicitation_id": "rfp-2026-001"},
    )
    queue_response = client.get("/api/v1/civicprocure/staff/reviews", headers=headers)
    summary_response = client.get("/api/v1/civicprocure/staff/reviews/summary", headers=headers)

    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL")
    monkeypatch.delenv("CIVICPROCURE_STAFF_API_KEY")

    assert rfp.status_code == 200
    assert rfp.json()["staff_review_id"]
    assert packet.status_code == 200
    assert packet.json()["staff_review_id"]
    assert queue_response.status_code == 200
    items = queue_response.json()["items"]
    assert len(items) == 2
    assert {item["review_id"] for item in items} == {
        rfp.json()["staff_review_id"],
        packet.json()["staff_review_id"],
    }
    assert summary_response.status_code == 200
    assert summary_response.json()["open_items"] == 2
    db_path.unlink()


def test_staff_review_queue_lifecycle_is_staff_gated_and_persistent(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicprocure-staff-review-lifecycle.db"
    monkeypatch.setenv(
        "CIVICPROCURE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}"
    )
    monkeypatch.setenv("CIVICPROCURE_STAFF_API_KEY", "test-staff-key")
    _dispose_workpaper_repository()

    headers = {"X-CivicProcure-Role": "staff", "X-CivicProcure-Staff-Key": "test-staff-key"}
    blocked = client.post(
        "/api/v1/civicprocure/staff/reviews",
        json={
            "solicitation_id": "rfp-2026-002",
            "procurement_title": "Street sweeper RFP",
            "reason": "Exceptions require review.",
        },
    )
    created = client.post(
        "/api/v1/civicprocure/staff/reviews",
        headers=headers,
        json={
            "solicitation_id": "rfp-2026-002",
            "procurement_title": "Street sweeper RFP",
            "reason": "Exceptions require review.",
        },
    )
    review_id = created.json()["review_id"]
    invalid_update = client.patch(
        f"/api/v1/civicprocure/staff/reviews/{review_id}",
        headers=headers,
        json={"status": "resolved"},
    )
    resolved = client.patch(
        f"/api/v1/civicprocure/staff/reviews/{review_id}",
        headers=headers,
        json={"status": "resolved", "assigned_to": "purchasing", "resolution": "Reviewed."},
    )

    _dispose_workpaper_repository()
    reloaded = client.get("/api/v1/civicprocure/staff/reviews?status=resolved", headers=headers)

    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL")
    monkeypatch.delenv("CIVICPROCURE_STAFF_API_KEY")

    assert blocked.status_code == 403
    assert "X-CivicProcure-Role" in blocked.json()["detail"]["fix"]
    assert created.status_code == 200
    assert created.json()["status"] == "open"
    assert invalid_update.status_code == 422
    assert "resolution is required" in invalid_update.json()["detail"]["fix"]
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"
    assert reloaded.status_code == 200
    assert reloaded.json()["items"][0]["review_id"] == review_id
    db_path.unlink()


def test_default_local_database_supports_staff_review_queue(monkeypatch) -> None:
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL", raising=False)
    monkeypatch.setenv("CIVICPROCURE_STAFF_API_KEY", "test-staff-key")
    _dispose_workpaper_repository()

    rfp = client.post(
        "/api/v1/civicprocure/rfps/draft",
        json={
            "procurement_title": "Default local RFP",
            "procurement_type": "professional services",
            "city_need": "Local workpaper persistence needs review.",
        },
    )
    response = client.get(
        "/api/v1/civicprocure/staff/reviews",
        headers={"X-CivicProcure-Role": "staff", "X-CivicProcure-Staff-Key": "test-staff-key"},
    )

    monkeypatch.delenv("CIVICPROCURE_STAFF_API_KEY")

    assert rfp.status_code == 200
    assert rfp.json()["draft_id"]
    assert rfp.json()["staff_review_id"]
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["procurement_title"] == "Default local RFP"


def test_get_rfp_missing_default_local_id_returns_actionable_404(monkeypatch) -> None:
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()
    response = client.get("/api/v1/civicprocure/rfps/draft/example")
    assert response.status_code == 404
    assert "POST /api/v1/civicprocure/rfps/draft" in response.json()["detail"]["fix"]


def test_get_award_packet_missing_id_returns_actionable_404(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicprocure-missing.db"
    monkeypatch.setenv(
        "CIVICPROCURE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}"
    )
    _dispose_workpaper_repository()
    response = client.get("/api/v1/civicprocure/award-packet/missing")
    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL")

    assert response.status_code == 404
    assert "POST /api/v1/civicprocure/award-packet" in response.json()["detail"]["fix"]
    db_path.unlink()
