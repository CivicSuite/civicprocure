# CivicProcure Production-Depth Workpaper Persistence

## Summary

CivicProcure now supports optional SQLAlchemy-backed persistence for generated RFP drafts and award-packet checklists. The feature is controlled by `CIVICPROCURE_WORKPAPER_DB_URL`; when it is absent, existing POST endpoints remain stateless and retrieval endpoints return actionable setup guidance.

## Shipped

- `ProcureWorkpaperRepository` with SQLite/local and schema-aware database support.
- Persisted RFP draft records with `draft_id` retrieval.
- Persisted award-packet records with `packet_id` retrieval.
- API round-trip tests, repository reload tests, and no-config/missing-record error tests.
- Current-facing README, manual, changelog, and landing-page updates.

## Verification

- `python -m pytest --collect-only -q`
- `python -m pytest -q`
- `bash scripts/verify-release.sh`
- Browser QA desktop/mobile for `/docs/index.html`.

## Boundary

CivicProcure still does not evaluate vendors, award contracts, submit procurements, provide legal advice, call live LLMs, use live vendor portals, or replace the procurement system of record.
