CivicProcure
=============

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, staff review queues, review-required CivicClerk/CivicContracts context packets, adversarial local integration mocks, and award-packet checklists.

Current state: v0.2.0 procurement support and staff review queue runtime. It ships a FastAPI package aligned to the published CivicCore v1.0.0 release wheel, deterministic and database-backed RFP drafting, award-packet workpapers, staff-only review queue workflows, review-required context packets, adversarial local integration mocks, proposal comparison scaffolds, exception extraction, scoring summary helper, award-packet checklist, and accessible public sample UI at /civicprocure.

It does not evaluate vendors, award contracts, make award decisions, submit procurements, provide legal advice, call live LLMs, call live vendor portals, or replace a procurement system of record.

Staff routes require CIVICPROCURE_WORKPAPER_DB_URL plus CIVICPROCURE_STAFF_API_KEY and trusted headers:

- X-CivicProcure-Role: staff or service
- X-CivicProcure-Staff-Key: configured staff key

Local development:

python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v1.0/civiccore-1.0.0-py3-none-any.whl
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
