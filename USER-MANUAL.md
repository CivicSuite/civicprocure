# CivicProcure User Manual

## For Non-Technical Users

CivicProcure helps city staff keep solicitation drafts, proposal notes, exception flags, scoring summaries, staff review queues, board memo inputs, CivicClerk/CivicContracts context references, and award-packet records organized. It can draft an RFP outline, scaffold proposal comparison rows, flag common exception language, build a scoring summary, assemble an award-packet checklist, and expose API-backed public and staff UIs.

Current state: 0.2.0 local-first procurement support and staff review queue runtime. CivicProcure saves generated RFP drafts, award-packet checklists, and staff review queue records in a default local SQLite database unless IT configures `CIVICPROCURE_WORKPAPER_DB_URL` for an explicit database. Staff-only review routes also require `CIVICPROCURE_STAFF_API_KEY`. CivicProcure does not provide official vendor evaluation decisions, legal advice, live vendor portals, live LLM calls, e-procurement submission portals, award decisions, or procurement system-of-record updates. Staff own every decision.

## For IT and Technical Staff

CivicProcure is a FastAPI Python package pinned to the published `civiccore v1.2.0` release wheel. The current runtime exposes:

- `GET /`
- `GET /health`
- `GET /ready`
- `GET /api/v1/civicprocure/readiness`
- `GET /civicprocure`
- `GET /civicprocure/staff`
- `GET /api/v1/civicprocure/integration-contracts`
- `POST /api/v1/civicprocure/rfps/draft`
- `GET /api/v1/civicprocure/rfps/draft/{draft_id}`
- `POST /api/v1/civicprocure/proposals/compare`
- `POST /api/v1/civicprocure/proposals/exceptions`
- `POST /api/v1/civicprocure/scoring/summary`
- `POST /api/v1/civicprocure/award-packet`
- `GET /api/v1/civicprocure/award-packet/{packet_id}`
- `POST /api/v1/civicprocure/context/procurement-review`
- `POST /api/v1/civicprocure/integrations/mock/procurement-context`
- `POST /api/v1/civicprocure/staff/reviews`
- `GET /api/v1/civicprocure/staff/reviews`
- `PATCH /api/v1/civicprocure/staff/reviews/{review_id}`
- `GET /api/v1/civicprocure/staff/reviews/summary`

CivicProcure uses `CIVICPROCURE_DATA_DIR` for its default local SQLite-backed workpaper database, or `CIVICPROCURE_WORKPAPER_DB_URL` when IT needs an explicit SQLAlchemy database URL. Staff queue routes also require `CIVICPROCURE_STAFF_API_KEY`, `X-CivicProcure-Role: staff`, and `X-CivicProcure-Staff-Key` matching the configured key. CivicProcure uses CivicCore `staff_key_gate` for timing-safe key comparison.

Use `civicprocure-db-status` to initialize/check an explicit workpaper schema. `/ready` and `/api/v1/civicprocure/readiness` report ready when the local schema is available.

Run:

```bash
python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v1.2.0/civiccore-1.2.0-py3-none-any.whl
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## Architecture

```mermaid
flowchart LR
  Staff["Purchasing / finance / department leads"] --> CivicProcure["CivicProcure v0.2.0"]
  CivicProcure --> CivicCore["CivicCore v1.2.0"]
  CivicProcure -. released context ID .-> CivicClerk["CivicClerk v1.0.0"]
  CivicProcure -. future context ID .-> CivicContracts["CivicContracts"]
  CivicProcure --> Queue["Staff review queue"]
  CivicProcure --> Workpapers["RFP / award workpaper database"]
  CivicProcure --> Export["Award packet checklist"]
```

CivicProcure depends on CivicCore. CivicCore does not depend on CivicProcure. CivicProcure v0.2.0 uses local-first staff-gated persistence, review-required context packets for CivicClerk/CivicContracts references, staff review queue records, and adversarial local mocks for integration-depth validation.
