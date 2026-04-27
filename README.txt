CivicProcure
============

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, and award-packet checklists.

Current state: v0.1.0 procurement support foundation release. It ships deterministic sample helpers and an accessible public sample UI at /civicprocure.

Not shipped: live vendor portals, official vendor evaluation decisions, legal advice, live LLM calls, e-procurement submission portals, or procurement system-of-record integrations.

API surface:
- GET /
- GET /health
- GET /civicprocure
- POST /api/v1/civicprocure/rfps/draft
- POST /api/v1/civicprocure/proposals/compare
- POST /api/v1/civicprocure/proposals/exceptions
- POST /api/v1/civicprocure/scoring/summary
- POST /api/v1/civicprocure/award-packet

License: code Apache License 2.0; documentation CC BY 4.0.
