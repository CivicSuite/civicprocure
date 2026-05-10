# Changelog

## [0.2.0] - 2026-05-10

- Demoted the false v1.0.0 release label after the external CivicSuite audit found this module is a recovery/foundation module, not a canonical spec-complete v1 product.
- Preserved the useful recovery work while resetting the public package version to 0.2.0.
- Kept the CivicCore v1.0.0 wheel dependency and pinned it with SHA256 for release integrity.
- Supersedes the prior public v1.0.0 posture; do not treat v1.0.0 as production-ready or spec-complete.

All notable changes to CivicProcure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-05-09

### Added

- CivicCore v1.0.0 release-wheel alignment.
- Staff-only procurement review queue workflows protected by `CIVICPROCURE_STAFF_API_KEY`.
- Review-required CivicClerk/CivicContracts procurement context endpoint.
- Adversarial local integration mocks for spoofed roles, official evaluation attempts, award-decision attempts, procurement submission attempts, legal-advice claims, stale context, and live vendor-portal claims.
- v1.0.0 docs, tests, browser QA evidence, release verification, and installer-integration requirement tracking.

### Changed

- Public UI and runtime health/version surfaces now report the CivicProcure v0.2.0 productization lane.

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
