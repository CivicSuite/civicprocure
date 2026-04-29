# Changelog

All notable changes to CivicProcure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] - 2026-04-28

### Changed

- Aligned CivicProcure to `civiccore==0.3.0`.
- Updated current-facing docs, release gate, CI wheel install, health/version tests, and browser QA evidence for the v0.1.1 compatibility release.
- Added optional SQLAlchemy-backed RFP draft and award-packet workpaper persistence behind `CIVICPROCURE_WORKPAPER_DB_URL`, with retrieval endpoints and actionable setup errors.

## [0.1.0] - 2026-04-27

### Added

- FastAPI package/runtime foundation pinned to `civiccore==0.2.0`.
- RFP drafting helper using deterministic sample data.
- proposal comparison helper with staff-verification boundary.
- exception extraction helper with review-required boundary.
- scoring summary helper.
- Award-packet checklist for procurement records.
- Accessible public sample UI at `/civicprocure` with browser QA coverage.
- Release gate: tests, docs, placeholder import guard, Ruff, and build artifact checks.

### Not Shipped

- live vendor portals, official vendor evaluation decisions, legal advice, live LLM calls, e-procurement submission portals, and procurement system-of-record integrations.
