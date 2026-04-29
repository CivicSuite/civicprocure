CivicProcure
============

CivicProcure is the CivicSuite module for procurement RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, and award-packet checklists.

Current state: v0.1.1 procurement support foundation release. It ships deterministic sample helpers, optional database-backed RFP/award workpapers, and an accessible public sample UI at /civicprocure, aligned to civiccore==0.3.0.

Not shipped: live vendor portals, official vendor evaluation decisions, legal advice, live LLM calls, e-procurement submission portals, or procurement system-of-record integrations.

API surface:
- GET /
- GET /health
- GET /civicprocure
- POST /api/v1/civicprocure/rfps/draft
- GET /api/v1/civicprocure/rfps/draft/{draft_id}
- POST /api/v1/civicprocure/proposals/compare
- POST /api/v1/civicprocure/proposals/exceptions
- POST /api/v1/civicprocure/scoring/summary
- POST /api/v1/civicprocure/award-packet
- GET /api/v1/civicprocure/award-packet/{packet_id}

Optional workpaper persistence: set CIVICPROCURE_WORKPAPER_DB_URL to a SQLAlchemy database URL to store generated RFP drafts and award-packet checklists. Without that variable, POST endpoints stay stateless and GET retrieval endpoints return an actionable setup message.

License: code Apache License 2.0; documentation CC BY 4.0.
