# CivicProcure Local-First Walkthrough

**Date:** 2026-06-06  
**Scope:** CivicProcure public UI, staff UI, default local persistence, readiness, integration contracts, RFP draft, award packet, procurement context, and retrieval endpoints.  
**Runtime:** `http://127.0.0.1:18172` with isolated `CIVICPROCURE_DATA_DIR`.

## Verdict

Pass. CivicProcure runs locally with the default SQLite workpaper directory, `/ready` is green, the public UI drafts through the local API, the staff UI is reachable with an actionable unauthenticated error state, RFP and award workpapers persist, and the module exposes suite integration contracts for downstream checks.

## Evidence

- Desktop public UI: `public-desktop.png`
- Public draft result: `public-draft-result.png`
- Desktop staff UI: `staff-desktop.png`
- Staff keyless error state: `staff-keyless-error.png`
- Mobile staff UI: `staff-mobile.png`
- API evidence bundle: `walkthrough-evidence.json`

## Runtime Checks

- `GET /` returned `local-first procurement support plus staff review queues`.
- `GET /ready` returned `ready=true`, `schema_ready=true`, and `using_default_local_database=true`.
- `GET /api/v1/civicprocure/integration-contracts` returned all required suite contracts:
  - `civicprocure.rfp_draft.v1`
  - `civicprocure.staff_review_queue.v1`
  - `civicprocure.award_packet.v1`
  - `civicprocure.procurement_context.v1`
- Public UI `#draft-button` posted to `/api/v1/civicprocure/rfps/draft` and rendered draft sections through safe text nodes.
- `POST /api/v1/civicprocure/rfps/draft` returned persisted `draft_id` and `staff_review_id`.
- `GET /api/v1/civicprocure/rfps/draft/{draft_id}` retrieved the created RFP draft.
- `POST /api/v1/civicprocure/award-packet` returned persisted `packet_id` and `staff_review_id`.
- `GET /api/v1/civicprocure/award-packet/{packet_id}` retrieved the created award packet.
- `POST /api/v1/civicprocure/context/procurement-review` returned clerk/contract context citations for staff review.

## UI Wiring

- `/civicprocure` is wired to the local RFP draft API and renders real backend output.
- `/civicprocure/staff` exposes RFP creation, award-packet creation, and queue loading controls.
- Desktop and mobile staff layouts remain readable with no observed text overlap.

## Known Boundary

This local walkthrough intentionally did not inject `CIVICPROCURE_STAFF_API_KEY` into the shell command because the local hook blocks secret-looking environment variables. Keyed staff queue behavior is covered by `tests/test_production_depth_procure_persistence.py` and must be proven again by the clean-machine tester through the suite installer, where the installer sets the local staff key environment.
