from __future__ import annotations

import pytest

import civicprocure.main as main_module


@pytest.fixture(autouse=True)
def isolated_civicprocure_runtime_data(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Keep default local-first runtime data isolated per test."""

    monkeypatch.setenv("CIVICPROCURE_DATA_DIR", str(tmp_path / "runtime-data"))
    yield
    main_module._dispose_workpaper_repository()
    main_module._workpaper_db_url = None

