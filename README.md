# CivicProcure

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, staff review queues, review-required CivicClerk/CivicContracts context packets, adversarial local integration mocks, and award-packet checklists.

Current state: **v0.2.0 local-first procurement support and staff review queue runtime**. This repo ships a FastAPI package aligned to the published CivicCore v1.2.0 release wheel, health/root endpoints, documentation gates, default local SQLite-backed RFP drafting, award-packet workpapers, staff-only review queue workflows, review-required CivicClerk/CivicContracts procurement context packets, adversarial local integration mocks, proposal comparison scaffolds, exception extraction, scoring summary helper, award-packet checklist, an accessible public sample UI at `/civicprocure`, and a staff review UI at `/civicprocure/staff`. It does **not** ship live vendor portals, official vendor evaluation decisions, legal advice, live LLM calls, e-procurement submission portals, award decisions, or procurement system-of-record integrations.

## What CivicProcure Does

- Draft sample RFP outlines and recommend a staff owner.
- Scaffold neutral proposal comparison rows for staff review.
- Flag common proposal exception language for staff/legal review.
- Build scoring summary scaffolds without ranking vendors.
- Produce award-packet checklists for procurement records.
- Persist RFP drafts, award-packet workpapers, and staff review items in the default local CivicProcure database.
- Route procurement review work through staff-only queue endpoints protected by `CIVICPROCURE_STAFF_API_KEY`.
- Carry CivicClerk, CivicContracts, and solicitation context IDs into review-required packets without calling those systems live.
- Validate adversarial local integration mocks for spoofed roles, official evaluation attempts, award-decision attempts, submission attempts, legal-advice claims, stale context, and live vendor-portal claims.
- Demonstrate API-backed public and staff procurement-support UIs at `/civicprocure` and `/civicprocure/staff`.

## What CivicProcure Does Not Do

- It does not evaluate vendors.
- It does not award contracts or make award decisions.
- It does not submit procurements.
- It does not provide legal advice.
- It does not call live LLMs or live vendor portals in this recovery release.
- It does not replace a procurement system of record.

## CivicCore Dependency

CivicProcure installs against the published CivicCore v1.2.0 release wheel:

```bash
python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v1.2.0/civiccore-1.2.0-py3-none-any.whl
```

## API Surface

- `GET /` returns the shipped/planned boundary.
- `GET /health` returns package and CivicCore versions.
- `GET /ready` returns workpaper database readiness for installer and operator checks.
- `GET /api/v1/civicprocure/readiness` returns detailed schema readiness.
- `GET /civicprocure` returns the accessible public sample UI.
- `GET /civicprocure/staff` returns the accessible staff review queue UI.
- `GET /api/v1/civicprocure/integration-contracts` returns suite-visible contract metadata.
- `POST /api/v1/civicprocure/rfps/draft` returns sample RFP drafting plus persisted `draft_id` and `staff_review_id`.
- `GET /api/v1/civicprocure/rfps/draft/{draft_id}` retrieves a persisted RFP draft.
- `POST /api/v1/civicprocure/proposals/compare` returns proposal comparison rows.
- `POST /api/v1/civicprocure/proposals/exceptions` returns exception flags.
- `POST /api/v1/civicprocure/scoring/summary` returns scoring-summary sections.
- `POST /api/v1/civicprocure/award-packet` returns an award-packet checklist plus persisted `packet_id` and `staff_review_id`.
- `GET /api/v1/civicprocure/award-packet/{packet_id}` retrieves a persisted award-packet checklist.
- `POST /api/v1/civicprocure/context/procurement-review` returns review-required procurement context with optional CivicClerk/CivicContracts IDs.
- `POST /api/v1/civicprocure/integrations/mock/procurement-context` validates local adversarial integration payloads.
- `POST /api/v1/civicprocure/staff/reviews` creates a staff-only review queue item.
- `GET /api/v1/civicprocure/staff/reviews` lists staff-only review queue items.
- `PATCH /api/v1/civicprocure/staff/reviews/{review_id}` updates staff-only queue status, assignment, and resolution.
- `GET /api/v1/civicprocure/staff/reviews/summary` returns staff queue counts.

## Local Workpaper Persistence And Staff Queue

CivicProcure creates a default local SQLAlchemy-backed SQLite database at startup. Set `CIVICPROCURE_DATA_DIR` to choose the local data directory, or set `CIVICPROCURE_WORKPAPER_DB_URL` when a city needs an explicit SQLAlchemy database URL. `/ready` is usable for clerk-first installation checks once the local schema is ready.

```bash
export CIVICPROCURE_DATA_DIR="./data/civicprocure"
```

Set `CIVICPROCURE_STAFF_API_KEY` before using staff-only review routes:

```bash
export CIVICPROCURE_STAFF_API_KEY="replace-with-city-secret"
```

Staff routes require `X-CivicProcure-Role: staff` and `X-CivicProcure-Staff-Key` matching the configured key. CivicProcure uses CivicCore `staff_key_gate` for timing-safe key comparison. Use `civicprocure-db-status` to initialize/check an explicit database URL when IT replaces the default local database.

## Local Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## License

Code is Apache License 2.0. Documentation is CC BY 4.0.
