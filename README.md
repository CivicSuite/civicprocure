# CivicProcure

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, staff review queues, review-required CivicClerk/CivicContracts context packets, adversarial local integration mocks, and award-packet checklists.

Current state: **v1.0.0 procurement support and staff review queue runtime**. This repo ships a FastAPI package aligned to the published CivicCore v1.0.0 release wheel, health/root endpoints, documentation gates, deterministic and database-backed RFP drafting, award-packet workpapers, staff-only review queue workflows, review-required CivicClerk/CivicContracts procurement context packets, adversarial local integration mocks, proposal comparison scaffolds, exception extraction, scoring summary helper, award-packet checklist, and accessible public sample UI at `/civicprocure`. It does **not** ship live vendor portals, official vendor evaluation decisions, legal advice, live LLM calls, e-procurement submission portals, award decisions, or procurement system-of-record integrations.

## What CivicProcure Does

- Draft sample RFP outlines and recommend a staff owner.
- Scaffold neutral proposal comparison rows for staff review.
- Flag common proposal exception language for staff/legal review.
- Build scoring summary scaffolds without ranking vendors.
- Produce award-packet checklists for procurement records.
- Persist RFP drafts and award-packet workpapers when `CIVICPROCURE_WORKPAPER_DB_URL` is configured.
- Route procurement review work through staff-only queue endpoints protected by `CIVICPROCURE_STAFF_API_KEY`.
- Carry CivicClerk, CivicContracts, and solicitation context IDs into review-required packets without calling those systems live.
- Validate adversarial local integration mocks for spoofed roles, official evaluation attempts, award-decision attempts, submission attempts, legal-advice claims, stale context, and live vendor-portal claims.
- Demonstrate a public procurement-support UI at `/civicprocure`.

## What CivicProcure Does Not Do

- It does not evaluate vendors.
- It does not award contracts or make award decisions.
- It does not submit procurements.
- It does not provide legal advice.
- It does not call live LLMs or live vendor portals in v1.0.0.
- It does not replace a procurement system of record.

## CivicCore Dependency

CivicProcure installs against the published CivicCore v1.0.0 release wheel:

```bash
python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v1.0/civiccore-1.0.0-py3-none-any.whl
```

## API Surface

- `GET /` returns the shipped/planned boundary.
- `GET /health` returns package and CivicCore versions.
- `GET /civicprocure` returns the accessible public sample UI.
- `POST /api/v1/civicprocure/rfps/draft` returns sample RFP drafting and a `staff_review_id` when persistence is configured.
- `GET /api/v1/civicprocure/rfps/draft/{draft_id}` retrieves a persisted RFP draft when workpaper persistence is configured.
- `POST /api/v1/civicprocure/proposals/compare` returns proposal comparison rows.
- `POST /api/v1/civicprocure/proposals/exceptions` returns exception flags.
- `POST /api/v1/civicprocure/scoring/summary` returns scoring-summary sections.
- `POST /api/v1/civicprocure/award-packet` returns an award-packet checklist and a `staff_review_id` when persistence is configured.
- `GET /api/v1/civicprocure/award-packet/{packet_id}` retrieves a persisted award-packet checklist when workpaper persistence is configured.
- `POST /api/v1/civicprocure/context/procurement-review` returns review-required procurement context with optional CivicClerk/CivicContracts IDs.
- `POST /api/v1/civicprocure/integrations/mock/procurement-context` validates local adversarial integration payloads.
- `POST /api/v1/civicprocure/staff/reviews` creates a staff-only review queue item.
- `GET /api/v1/civicprocure/staff/reviews` lists staff-only review queue items.
- `PATCH /api/v1/civicprocure/staff/reviews/{review_id}` updates staff-only queue status, assignment, and resolution.
- `GET /api/v1/civicprocure/staff/reviews/summary` returns staff queue counts.

## Optional Workpaper Persistence And Staff Queue

Set `CIVICPROCURE_WORKPAPER_DB_URL` to a SQLAlchemy database URL to store generated RFP drafts, award-packet checklists, and staff review queue records:

```bash
export CIVICPROCURE_WORKPAPER_DB_URL="sqlite+pysqlite:///./civicprocure.db"
```

Set `CIVICPROCURE_STAFF_API_KEY` before using staff-only review routes:

```bash
export CIVICPROCURE_STAFF_API_KEY="replace-with-city-secret"
```

Staff routes require `X-CivicProcure-Role: staff` or `service` and `X-CivicProcure-Staff-Key` matching the configured key. Without persistence, CivicProcure remains deterministic and stateless. Retrieval and staff-only endpoints return actionable `503` responses that name the required configuration.

## Local Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## License

Code is Apache License 2.0. Documentation is CC BY 4.0.
