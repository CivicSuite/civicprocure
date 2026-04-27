# CivicProcure Agent Contract

## Source of Truth

- Upstream suite spec: `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md`, especially the CivicProcure catalog entry and suite-wide non-negotiables.
- CivicProcure supports RFP drafting, proposal comparison, exception extraction, scoring summaries, board memo inputs, and award-packet checklists.
- Staff own every decision.

## Hard Boundaries

- CivicProcure never evaluates vendors, awards contracts, submits procurements, provides legal advice, or updates a procurement system of record.
- CivicProcure v0.1.0 must not call live LLMs or live vendor portals.
- Proposal comparisons, exception flags, scoring summaries, and award packets must be marked staff-review-required where applicable.
- CivicProcure depends on CivicCore; CivicCore must never depend on CivicProcure.
- CivicProcure may reference CivicClerk, CivicContracts, and CivicRecords concepts only through released contracts or deterministic sample data in v0.1.0.

## Verification

Run `bash scripts/verify-release.sh` before every push or release.
