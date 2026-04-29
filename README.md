# CivicProcure

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, and award-packet checklists.

Current state: **v0.1.1 procurement support foundation release**. This repo ships a FastAPI package, health/root endpoints, documentation gates, deterministic sample RFP drafting, proposal comparison, exception extraction helper, scoring summary helper, award-packet checklist, optional database-backed RFP/award workpapers, and accessible public sample UI at `/civicprocure`, aligned to `civiccore==0.3.0`. It does **not** ship live vendor portals, official vendor evaluation decisions, legal advice, live LLM calls, e-procurement submission portals, or procurement system-of-record integrations.

## What CivicProcure Does

- Draft sample RFP outlines and recommend a staff owner.
- Scaffold neutral proposal comparison rows for staff review.
- Flag common proposal exception language for staff/legal review.
- Build scoring summary scaffolds without ranking vendors.
- Produce award-packet checklists for procurement records.
- Persist RFP drafts and award-packet workpapers when `CIVICPROCURE_WORKPAPER_DB_URL` is configured.
- Demonstrate a public procurement-support UI at `/civicprocure`.

## What CivicProcure Does Not Do

- It does not evaluate vendors.
- It does not award contracts or submit procurements.
- It does not provide legal advice.
- It does not call live LLMs in v0.1.1.
- It does not replace a procurement system of record.

## API Surface

- `GET /` returns the shipped/planned boundary.
- `GET /health` returns package and CivicCore versions.
- `GET /civicprocure` returns the accessible public sample UI.
- `POST /api/v1/civicprocure/rfps/draft` returns sample RFP drafting.
- `GET /api/v1/civicprocure/rfps/draft/{draft_id}` retrieves a persisted RFP draft when workpaper persistence is configured.
- `POST /api/v1/civicprocure/proposals/compare` returns proposal comparison rows.
- `POST /api/v1/civicprocure/proposals/exceptions` returns exception flags.
- `POST /api/v1/civicprocure/scoring/summary` returns scoring-summary sections.
- `POST /api/v1/civicprocure/award-packet` returns an award-packet checklist.
- `GET /api/v1/civicprocure/award-packet/{packet_id}` retrieves a persisted award-packet checklist when workpaper persistence is configured.

## Optional Workpaper Persistence

Set `CIVICPROCURE_WORKPAPER_DB_URL` to a SQLAlchemy database URL to store generated RFP drafts and award-packet checklists for later review. If the variable is not set, POST endpoints remain stateless and return `draft_id` / `packet_id` as `null`; GET retrieval endpoints return an actionable `503` explaining how to enable persistence.

## Local Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## License

Code is Apache License 2.0. Documentation is CC BY 4.0.
