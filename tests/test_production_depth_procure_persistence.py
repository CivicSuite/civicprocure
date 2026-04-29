from __future__ import annotations

from pathlib import Path

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


def test_get_rfp_without_persistence_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICPROCURE_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()
    response = client.get("/api/v1/civicprocure/rfps/draft/example")
    assert response.status_code == 503
    assert "Set CIVICPROCURE_WORKPAPER_DB_URL" in response.json()["detail"]["fix"]


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
