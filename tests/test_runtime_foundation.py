from fastapi.testclient import TestClient

import civicprocure
from civicprocure.main import app


client = TestClient(app)


def test_package_version_is_010() -> None:
    assert civicprocure.__version__ == "0.1.0"


def test_root_endpoint_states_runtime_boundary() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "CivicProcure"
    assert payload["version"] == "0.1.0"
    assert payload["status"] == "procurement support foundation"
    assert "official vendor evaluation decisions" in payload["message"]
    assert "not implemented yet" in payload["message"]
    assert payload["next_step"].startswith("Post-v0.1.0 roadmap")


def test_health_endpoint_reports_versions() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "civicprocure"
    assert payload["version"] == "0.1.0"
    assert payload["civiccore_version"] == "0.2.0"
