CivicProcure
=============

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, staff review queues, review-required CivicClerk/CivicContracts context packets, adversarial local integration mocks, and award-packet checklists.

Current state: v0.2.0 local-first procurement support and staff review queue runtime. It ships a FastAPI package aligned to the published CivicCore v1.2.0 release wheel, default local database-backed RFP drafting, award-packet workpapers, staff-only review queue workflows, review-required context packets, adversarial local integration mocks, proposal comparison scaffolds, exception extraction, scoring summary helper, award-packet checklist, an API-backed accessible public sample UI at /civicprocure, and a staff UI at /civicprocure/staff.

It does not evaluate vendors, award contracts, make award decisions, submit procurements, provide legal advice, call live LLMs, call live vendor portals, or replace a procurement system of record.

Staff routes require CIVICPROCURE_STAFF_API_KEY and trusted headers:

- X-CivicProcure-Role: staff or service
- X-CivicProcure-Staff-Key: configured staff key

CivicProcure creates a default local SQLite workpaper database. Set CIVICPROCURE_DATA_DIR to choose its location, or set CIVICPROCURE_WORKPAPER_DB_URL for an explicit SQLAlchemy database URL. Use civicprocure-db-status to initialize/check explicit schema.

Local development:

python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v1.2.0/civiccore-1.2.0-py3-none-any.whl
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
